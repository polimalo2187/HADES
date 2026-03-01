# engine/signal_generator.py

from __future__ import annotations

from datetime import datetime, timedelta
from core.logger import get_logger
from core.config import Config
from core.constants import (
    PLAN_FREE,
    PLAN_PLUS,
    PLAN_PREMIUM,
    SIGNAL_ACTIVE,
)

logger = get_logger(__name__)


class SignalGenerator:
    """
    Genera señales finales a partir del score y los indicadores.

    - Score SIEMPRE es 0..1
    - Direcciones: BUY / SELL
    - TP/SL usan ATR (en precio) para evitar incoherencias por símbolo
    """

    def __init__(self):
        self.cfg = Config()
        logger.info("SignalGenerator inicializado")

    def generate(self, pair: str, candles: list, indicators: dict, score: float):
        """
        Genera una señal SOLO si el score alcanza el mínimo requerido.
        """
        plan = self._classify_plan(score)
        if not plan:
            return None

        if not candles:
            return None

        last_candle = candles[-1]
        entry_price = float(last_candle["close"])

        direction = indicators.get("trend", "NEUTRAL")
        if direction not in ("BUY", "SELL"):
            return None

        atr_price = float(indicators.get("atr", 0.0))
        if atr_price <= 0:
            return None

        tp, sl = self._compute_tp_sl(entry_price, direction, atr_price, plan)

        signal = {
            "id": self._generate_signal_id(pair),
            "pair": pair,
            "direction": direction,
            "score": float(score),
            "plan": plan,
            "entry": float(entry_price),
            "tp": float(tp),
            "sl": float(sl),
            "timeframe": indicators.get("timeframe", self.cfg.TIMEFRAME_SIGNAL),
            "confidence": self._confidence_label(score),
            "created_at": datetime.utcnow(),
            "expires_at": self._expiration_time(plan),
            "status": SIGNAL_ACTIVE,
        }

        logger.info(f"🎯 Señal generada | {pair} | {direction} | {plan} | Score {score:.3f}")
        return signal

    # ─────────────────────────────
    # Clasificación de señal (score 0..1)
    # ─────────────────────────────

    def _classify_plan(self, score: float) -> str | None:
        score = float(score)
        if score >= self.cfg.MIN_SCORE_PREMIUM:
            return PLAN_PREMIUM
        elif score >= self.cfg.MIN_SCORE_PLUS:
            return PLAN_PLUS
        elif score >= self.cfg.MIN_SCORE_FREE:
            return PLAN_FREE
        return None

    def _confidence_label(self, score: float) -> str:
        score = float(score)
        if score >= self.cfg.MIN_SCORE_PREMIUM:
            return "EXTREMA"
        elif score >= self.cfg.MIN_SCORE_PLUS:
            return "ALTA"
        return "MEDIA"

    # ─────────────────────────────
    # Gestión de riesgo (TP/SL por dirección)
    # ─────────────────────────────

    def _compute_tp_sl(self, entry: float, direction: str, atr_price: float, plan: str):
        rr_map = {
            PLAN_FREE: 1.5,
            PLAN_PLUS: 2.5,
            PLAN_PREMIUM: 4.0,
        }
        sl_atr_map = {
            PLAN_FREE: 1.0,
            PLAN_PLUS: 0.8,
            PLAN_PREMIUM: 0.7,
        }

        rr = rr_map.get(plan, 1.5)
        sl_atr = sl_atr_map.get(plan, 1.0)

        if direction == "BUY":
            sl = entry - (sl_atr * atr_price)
            tp = entry + rr * (entry - sl)
        else:  # SELL
            sl = entry + (sl_atr * atr_price)
            tp = entry - rr * (sl - entry)

        # Redondeo simple (5 decimales funciona para la mayoría; brokers con JPY usan 3)
        return round(tp, 5), round(sl, 5)

    # ─────────────────────────────
    # Tiempo de vida de la señal
    # ─────────────────────────────

    def _expiration_time(self, plan: str):
        # Señales premium viven más; configurable si quieres.
        durations = {
            PLAN_FREE: timedelta(hours=2),
            PLAN_PLUS: timedelta(hours=4),
            PLAN_PREMIUM: timedelta(hours=8),
        }
        return datetime.utcnow() + durations.get(plan, timedelta(hours=self.cfg.SIGNAL_EXPIRATION_HOURS))

    # ─────────────────────────────
    # Utilidades
    # ─────────────────────────────

    def _generate_signal_id(self, pair: str) -> str:
        timestamp = datetime.utcnow().strftime("%Y%m%d%H%M%S")
        return f"HADES-{pair}-{timestamp}"
