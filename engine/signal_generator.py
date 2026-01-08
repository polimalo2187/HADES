# engine/signal_generator.py

from datetime import datetime, timedelta
from core.logger import get_logger
from core.constants import (
    SIGNAL_FREE,
    SIGNAL_PLUS,
    SIGNAL_PREMIUM,
)

logger = get_logger(__name__)


class SignalGenerator:
    """
    Genera señales finales a partir del score y los indicadores.
    Aquí se define la CALIDAD y la CLASIFICACIÓN por plan.
    """

    def __init__(self):
        logger.info("SignalGenerator inicializado")

    def generate(self, pair, candles, indicators, score):
        """
        Genera una señal SOLO si cumple estándares institucionales.
        """

        plan = self._classify_plan(score)
        if not plan:
            return None

        last_candle = candles[-1]
        entry_price = last_candle["close"]

        signal = {
            "id": self._generate_signal_id(pair),
            "pair": pair,
            "direction": indicators["trend"],
            "score": score,
            "plan": plan,
            "entry": entry_price,
            "tp": self._calculate_take_profit(entry_price, indicators, plan),
            "sl": self._calculate_stop_loss(entry_price, indicators, plan),
            "timeframe": indicators["timeframe"],
            "confidence": self._confidence_label(score),
            "created_at": datetime.utcnow(),
            "expires_at": self._expiration_time(plan),
            "status": "ACTIVE",
        }

        logger.info(
            f"🎯 Señal generada | {pair} | {signal['direction']} | {plan} | Score {score}"
        )

        return signal

    # ─────────────────────────────
    # Clasificación de señal
    # ─────────────────────────────

    def _classify_plan(self, score):
        """
        Define qué tipo de señal es según su score.
        """
        if score >= 90:
            return SIGNAL_PREMIUM
        elif score >= 80:
            return SIGNAL_PLUS
        elif score >= 70:
            return SIGNAL_FREE
        return None

    def _confidence_label(self, score):
        if score >= 90:
            return "EXTREMA"
        elif score >= 80:
            return "ALTA"
        return "MEDIA"

    # ─────────────────────────────
    # Gestión de riesgo
    # ─────────────────────────────

    def _calculate_take_profit(self, entry, indicators, plan):
        rr = {
            SIGNAL_FREE: 1.5,
            SIGNAL_PLUS: 2.5,
            SIGNAL_PREMIUM: 4.0,
        }[plan]

        return round(entry * (1 + rr * indicators["volatility"]), 5)

    def _calculate_stop_loss(self, entry, indicators, plan):
        sl_factor = {
            SIGNAL_FREE: 0.8,
            SIGNAL_PLUS: 0.6,
            SIGNAL_PREMIUM: 0.5,
        }[plan]

        return round(entry * (1 - sl_factor * indicators["volatility"]), 5)

    # ─────────────────────────────
    # Tiempo de vida de la señal
    # ─────────────────────────────

    def _expiration_time(self, plan):
        durations = {
            SIGNAL_FREE: timedelta(hours=2),
            SIGNAL_PLUS: timedelta(hours=4),
            SIGNAL_PREMIUM: timedelta(hours=8),
        }
        return datetime.utcnow() + durations[plan]

    # ─────────────────────────────
    # Utilidades
    # ─────────────────────────────

    def _generate_signal_id(self, pair):
        timestamp = datetime.utcnow().strftime("%Y%m%d%H%M%S")
        return f"HADES-{pair}-{timestamp}"
