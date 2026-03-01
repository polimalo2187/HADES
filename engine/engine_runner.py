# engine/engine_runner.py

import time

from core.logger import get_logger
from core.constants import PLAN_FREE, PLAN_PLUS, PLAN_PREMIUM
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
    TOTALMENTE independiente de Telegram.
    """

    def __init__(self, interval_seconds: int = 60):
        self.interval_seconds = interval_seconds
        self.running = False

        self.market_data = MarketDataProvider()
        self.indicators = IndicatorEngine()
        self.scorer = SignalScorer()
        self.generator = SignalGenerator()
        self.signal_repo = SignalRepository()
        self.signal_cleanup = SignalCleanup()

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

    def run_cycle(self):
        logger.info("🔁 Iniciando ciclo de análisis")

        # 1) Limpieza
        self.signal_cleanup.cleanup_expired_signals()

        # 2) estado por plan
        active_plans = {
            PLAN_FREE: self.signal_repo.get_active_signal_by_plan(PLAN_FREE),
            PLAN_PLUS: self.signal_repo.get_active_signal_by_plan(PLAN_PLUS),
            PLAN_PREMIUM: self.signal_repo.get_active_signal_by_plan(PLAN_PREMIUM),
        }

        # 3) analizar pares
        for pair in self.market_data.get_supported_pairs():
            candles = self.market_data.fetch_latest_data(pair)

            if not candles or len(candles) < 60:
                continue

            indicators = self.indicators.calculate(candles)
            score = self.scorer.score(indicators)

            if not self.scorer.is_tradeable(score):
                continue

            signal = self.generator.generate(
                pair=pair,
                candles=candles,
                indicators=indicators,
                score=score,
            )

            if not signal:
                continue

            plan = signal["plan"]

            # 4) evitar solapamiento por plan
            if active_plans.get(plan):
                continue

            self.signal_repo.save_new_signal(signal)
            active_plans[plan] = signal

            logger.info(f"🚨 Señal {plan.upper()} generada | {pair} | Score {score:.3f}")

            if all(active_plans.values()):
                break

        logger.info("✅ Ciclo finalizado")


# ─────────────────────────────────────────────────────────────
# WRAPPER para scheduler/jobs.py
# ─────────────────────────────────────────────────────────────

_engine_singleton = EngineRunner(interval_seconds=60)


def run_engine():
    """
    Ejecuta un ciclo único del motor. Usado por scheduler/jobs.py
    """
    return _engine_singleton.run_cycle()
