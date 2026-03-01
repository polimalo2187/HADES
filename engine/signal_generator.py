# engine/signal_generator.py

from __future__ import annotations

from datetime import datetime, timedelta

from core.logger import get_logger
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
    Score esperado: 0..1
    """

    def __init__(self):
        logger.info("SignalGenerator inicializado")

    def generate(self, pair, candles, indicators, score):
        plan = self._classify_plan(score)
        if not plan:
            return None

        last_candle = candles[-1]
        entry_price = float(last_candle["close"])

        direction = indicators.get("trend", "NEUTRAL")
        if direction not in ("BUY", "SELL"):
            return None

        # SL/TP simples basados en ATR (si no hay ATR, fallback)
        atr = float(indicators.get("atr", 0.0) or 0.0)
        if atr <= 0:
            atr = max(entry_price * 0.001, 0.0001)

        tp, sl = self._compute_tp_sl(entry_price, direction, atr, plan)

        signal = {
            "id": self._generate_signal_id(pair),
            "pair": pair,
            "direction": direction,
            "score": float(score),
            "plan": plan,
            "entry": float(entry_price),
            "tp": float(tp),
            "sl": float(sl),
            "timeframe": indicators.get("timeframe", "M15"),
            "confidence": self._confidence_label(score),
            "created_at": datetime.utcnow(),
            "expires_at": self._expiration_time(plan),
            "status": SIGNAL_ACTIVE,
        }

        logger.info(f"🎯 Señal generada | {pair} | {direction} | {plan} | Score {score:.3f}")
        return signal

    def _classify_plan(self, score: float):
        """
        Score 0..1:
          >=0.90 premium
          >=0.80 plus
          >=0.70 free
        """
        s = float(score)
        if s >= 0.90:
            return PLAN_PREMIUM
        if s >= 0.80:
            return PLAN_PLUS
        if s >= 0.70:
            return PLAN_FREE
        return None

    def _confidence_label(self, score: float):
        s = float(score)
        if s >= 0.90:
            return "EXTREMA"
        if s >= 0.80:
            return "ALTA"
        return "MEDIA"

    def _compute_tp_sl(self, entry: float, direction: str, atr: float, plan: str):
        # RR por plan (simple)
        rr_map = {PLAN_FREE: 1.5, PLAN_PLUS: 2.5, PLAN_PREMIUM: 4.0}
        sl_atr_map = {PLAN_FREE: 1.0, PLAN_PLUS: 0.8, PLAN_PREMIUM: 0.7}

        rr = rr_map.get(plan, 1.5)
        sl_atr = sl_atr_map.get(plan, 1.0)

        if direction == "BUY":
            sl = entry - (sl_atr * atr)
            tp = entry + rr * (entry - sl)
        else:  # SELL
            sl = entry + (sl_atr * atr)
            tp = entry - rr * (sl - entry)

        return round(tp, 5), round(sl, 5)

    def _expiration_time(self, plan: str):
        durations = {PLAN_FREE: 2, PLAN_PLUS: 4, PLAN_PREMIUM: 8}  # horas
        hours = durations.get(plan, 4)
        return datetime.utcnow() + timedelta(hours=hours)

    def _generate_signal_id(self, pair: str):
        timestamp = datetime.utcnow().strftime("%Y%m%d%H%M%S")
        return f"HADES-{pair}-{timestamp}"
