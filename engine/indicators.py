# engine/indicators.py

from typing import List
from core.logger import get_logger

logger = get_logger(__name__)


class Indicators:
    """
    Cálculo de indicadores técnicos.
    Todas las funciones trabajan sobre listas de precios.
    """

    @staticmethod
    def sma(values: List[float], period: int) -> float:
        if len(values) < period:
            return 0.0
        return sum(values[-period:]) / period

    @staticmethod
    def ema(values: List[float], period: int) -> float:
        if len(values) < period:
            return 0.0

        k = 2 / (period + 1)
        ema_value = values[0]

        for price in values[1:]:
            ema_value = price * k + ema_value * (1 - k)

        return ema_value

    @staticmethod
    def rsi(values: List[float], period: int = 14) -> float:
        if len(values) < period + 1:
            return 0.0

        gains = []
        losses = []

        for i in range(1, period + 1):
            delta = values[-i] - values[-i - 1]
            if delta >= 0:
                gains.append(delta)
            else:
                losses.append(abs(delta))

        average_gain = sum(gains) / period if gains else 0
        average_loss = sum(losses) / period if losses else 0

        if average_loss == 0:
            return 100.0

        rs = average_gain / average_loss
        rsi = 100 - (100 / (1 + rs))

        return rsi

    @staticmethod
    def atr(highs: List[float], lows: List[float], closes: List[float], period: int = 14) -> float:
        if len(closes) < period + 1:
            return 0.0

        true_ranges = []

        for i in range(1, period + 1):
            tr = max(
                highs[-i] - lows[-i],
                abs(highs[-i] - closes[-i - 1]),
                abs(lows[-i] - closes[-i - 1]),
            )
            true_ranges.append(tr)

        return sum(true_ranges) / period
