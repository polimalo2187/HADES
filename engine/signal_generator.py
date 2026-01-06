# engine/signal_generator.py

from core.logger import get_logger
from engine.indicators import Indicators
from engine.signal_scoring import SignalScoring

logger = get_logger(__name__)


class SignalGenerator:
    """
    Genera señales completas a partir de datos de mercado,
    indicadores técnicos y scoring.
    """

    def __init__(self):
        self.indicators = Indicators()
        self.scoring = SignalScoring()
        logger.info("SignalGenerator inicializado")

    def generate_signal(self, market_data: dict) -> dict | None:
        """
        Genera una señal estructurada.
        Retorna None si no cumple los criterios mínimos.
        """

        closes = market_data.get("closes", [])
        highs = market_data.get("highs", [])
        lows = market_data.get("lows", [])

        if len(closes) < 50:
            return None

        # ===============================
        # INDICADORES
        # ===============================
        ema_fast = self.indicators.ema(closes, 20)
        ema_slow = self.indicators.ema(closes, 50)
        rsi = self.indicators.rsi(closes)
        atr = self.indicators.atr(highs, lows, closes)

        # ===============================
        # MÉTRICAS NORMALIZADAS (0 - 1)
        # ===============================
        trend_strength = min(abs(ema_fast - ema_slow) / ema_slow, 1.0)
        volatility = min(atr / closes[-1], 1.0)
        momentum = min(abs(closes[-1] - closes[-10]) / closes[-10], 1.0)
        structure_quality = 0.8  # placeholder (estructura de mercado)

        rsi_score = 1 - abs(50 - rsi) / 50 if rsi else 0

        # ===============================
        # SCORE FINAL
        # ===============================
        score = self.scoring.calculate_score(
            trend_strength=trend_strength,
            rsi=rsi_score,
            volatility=volatility,
            momentum=momentum,
            structure_quality=structure_quality,
        )

        plan_level = self.scoring.classify_score(score)
        if plan_level == "discarded":
            return None

        # ===============================
        # PERFILES DE RIESGO
        # ===============================
        entry_price = closes[-1]

        signal = {
            "pair": market_data.get("pair"),
            "direction": "BUY" if ema_fast > ema_slow else "SELL",
            "score": score,
            "plan": plan_level,
            "profiles": {
                "conservative": {
                    "entry": entry_price,
                    "stop_loss": entry_price - atr * 1.5,
                    "take_profit": entry_price + atr * 2,
                },
                "moderate": {
                    "entry": entry_price,
                    "stop_loss": entry_price - atr * 1.2,
                    "take_profit": entry_price + atr * 3,
                },
                "aggressive": {
                    "entry": entry_price,
                    "stop_loss": entry_price - atr,
                    "take_profit": entry_price + atr * 4,
                },
            },
        }

        logger.info(
            f"Señal generada {signal['pair']} | {signal['direction']} | "
            f"Plan: {plan_level} | Score: {round(score, 3)}"
        )

        return signal
