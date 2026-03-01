# engine/engine_runner.py

from __future__ import annotations

import time
from datetime import datetime, timedelta
from statistics import median

from core.config import Config
from core.constants import PLAN_FREE, PLAN_PLUS, PLAN_PREMIUM
from core.logger import get_logger
from engine.market_data import MarketDataProvider
from engine.indicators import IndicatorEngine
from engine.signal_scoring import SignalScorer
from engine.signal_generator import SignalGenerator
from signal_manager.signal_repository import SignalRepository
from signal_manager.signal_cleanup import SignalCleanup

logger = get_logger(__name__)


class EngineRunner:
    """
    Ejecuta el motor de análisis de mercado 24/7.
    Modo alta efectividad:
      - Señal en H1 (bar close)
      - Filtro de tendencia en H4 (misma dirección)
      - Universo dinámico: top X% por tick_volume mediano
      - Filtro spread <= MAX_SPREAD_ATR_RATIO * ATR (en puntos)
      - Cooldown por símbolo para evitar spam
    """

    def __init__(self, interval_seconds: int = 60):
        self.cfg = Config()
        self.interval_seconds = interval_seconds
        self.running = False

        # Componentes del engine
        self.market_data = MarketDataProvider()
        self.indicators = IndicatorEngine(
            atr_period=self.cfg.ATR_PERIOD,
            rsi_period=14,
            ema_fast=50,
            ema_slow=200,
        )
        self.scorer = SignalScorer()
        self.generator = SignalGenerator()
        self.signal_repo = SignalRepository()
        self.signal_cleanup = SignalCleanup()

        # Cooldown por símbolo (en memoria)
        self._last_signal_time_by_pair: dict[str, datetime] = {}

    def start(self):
        logger.info("🔥 HADES Engine iniciado (modo 24/7)")
        self.running = True

        while self.running:
            try:
                self.run_cycle()
            except Exception as e:
                logger.exception(f"❌ Error en ciclo del engine: {e}")

            time.sleep(self.interval_seconds)

    def stop(self):
        self.running = False
        logger.info("🛑 HADES Engine detenido")

    def _cooldown_seconds(self) -> int:
        # Timeframe_signal por defecto H1
        tf = self.cfg.TIMEFRAME_SIGNAL.upper()
        tf_seconds = {
            "M1": 60,
            "M5": 300,
            "M15": 900,
            "M30": 1800,
            "H1": 3600,
            "H4": 14400,
            "D1": 86400,
        }.get(tf, 3600)
        return int(self.cfg.COOLDOWN_BARS * tf_seconds)

    def _is_in_cooldown(self, pair: str) -> bool:
        last = self._last_signal_time_by_pair.get(pair)
        if not last:
            return False
        return (datetime.utcnow() - last).total_seconds() < self._cooldown_seconds()

    def _mark_signal(self, pair: str):
        self._last_signal_time_by_pair[pair] = datetime.utcnow()

    def _select_tradeable_pairs(self) -> list[str]:
        """
        Selecciona el universo de pares:
        - Solo FX (según heurística de símbolo)
        - Datos suficientes en H1
        - Top X% por tick_volume mediano
        - Spread <= ratio * ATR (en puntos)
        """
        tf_sig = self.cfg.TIMEFRAME_SIGNAL

        pairs = self.market_data.get_supported_pairs()
        if not pairs:
            return []

        metrics = []
        for pair in pairs:
            candles = self.market_data.fetch_latest_data(pair, timeframe=tf_sig, limit=self.cfg.LIQUIDITY_BARS)
            if not candles or len(candles) < max(100, self.cfg.ATR_PERIOD + 10):
                continue

            # bar-close: quita vela viva
            if self.cfg.BAR_CLOSE_ONLY and len(candles) > 2:
                candles = candles[:-1]

            vols = [c.get("volume", 0.0) for c in candles if c.get("volume") is not None]
            if not vols:
                continue

            info = self.market_data.get_symbol_info(pair)
            if info is None or not getattr(info, "point", None) or not getattr(info, "spread", None):
                continue

            ind = self.indicators.calculate(candles, timeframe=tf_sig)
            atr_price = float(ind.get("atr", 0.0))
            if atr_price <= 0:
                continue

            atr_points = atr_price / float(info.point)
            spread_points = float(info.spread)

            metrics.append(
                {
                    "pair": pair,
                    "median_tick_volume": float(median(vols)),
                    "spread_points": spread_points,
                    "atr_points": float(atr_points),
                }
            )

        if not metrics:
            return []

        # Top X% por tick_volume
        metrics.sort(key=lambda x: x["median_tick_volume"], reverse=True)
        keep_n = max(1, int(len(metrics) * float(self.cfg.LIQUIDITY_TOP_PCT)))
        top = metrics[:keep_n]

        # Spread vs ATR filter
        tradeable = []
        for m in top:
            if m["atr_points"] <= 0:
                continue
            if m["spread_points"] <= (m["atr_points"] * float(self.cfg.MAX_SPREAD_ATR_RATIO)):
                tradeable.append(m["pair"])

        return tradeable

    def run_cycle(self):
        """
        Ciclo completo de análisis:
        - Limpia señales expiradas
        - Selecciona universo tradeable
        - Analiza H1 + filtro H4
        - Genera hasta 3 señales (una por plan) sin solapamiento
        """
        logger.info("🔁 Iniciando ciclo de análisis")

        # 1️⃣ Limpieza de señales expiradas
        self.signal_cleanup.cleanup_expired_signals()

        # 2️⃣ Estado actual por plan
        active_plans = {
            PLAN_FREE: self.signal_repo.get_active_signal_by_plan(PLAN_FREE),
            PLAN_PLUS: self.signal_repo.get_active_signal_by_plan(PLAN_PLUS),
            PLAN_PREMIUM: self.signal_repo.get_active_signal_by_plan(PLAN_PREMIUM),
        }

        # 3️⃣ Universo
        pairs = self._select_tradeable_pairs()
        logger.info(f"🧭 Universo tradeable: {len(pairs)} pares (TF {self.cfg.TIMEFRAME_SIGNAL})")

        tf_sig = self.cfg.TIMEFRAME_SIGNAL
        tf_trend = self.cfg.TIMEFRAME_TREND

        for pair in pairs:
            # Cooldown por símbolo (evita spam)
            if self._is_in_cooldown(pair):
                continue

            candles_sig = self.market_data.fetch_latest_data(pair, timeframe=tf_sig, limit=500)
            candles_trend = self.market_data.fetch_latest_data(pair, timeframe=tf_trend, limit=500)

            if not candles_sig or len(candles_sig) < 250:
                continue
            if not candles_trend or len(candles_trend) < 250:
                continue

            # bar-close: quita vela viva
            if self.cfg.BAR_CLOSE_ONLY:
                candles_sig = candles_sig[:-1]
                candles_trend = candles_trend[:-1]
                if len(candles_sig) < 200 or len(candles_trend) < 200:
                    continue

            ind_sig = self.indicators.calculate(candles_sig, timeframe=tf_sig)
            ind_trend = self.indicators.calculate(candles_trend, timeframe=tf_trend)

            # Filtro H4: misma dirección (alta efectividad)
            if ind_sig.get("trend") != ind_trend.get("trend"):
                continue

            # Score 0..1
            score = self.scorer.score(ind_sig)
            if not self.scorer.is_tradeable(score):
                continue

            signal = self.generator.generate(
                pair=pair,
                candles=candles_sig,
                indicators=ind_sig,
                score=score,
            )
            if not signal:
                continue

            plan = signal["plan"]

            # Evitar solapamiento por plan
            if active_plans.get(plan):
                continue

            self.signal_repo.save_new_signal(signal)
            active_plans[plan] = signal
            self._mark_signal(pair)

            logger.info(f"🚨 Señal {plan.upper()} generada | {pair} | Score {score:.3f}")

            # Si ya existen las 3 señales, terminamos
            if all(active_plans.values()):
                break

        logger.info("✅ Ciclo finalizado")
