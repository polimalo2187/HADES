# engine/indicators.py

from __future__ import annotations

from typing import List, Dict, Any
from core.logger import get_logger

logger = get_logger(__name__)


class Indicators:
    """
    Indicadores básicos.
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

        average_gain = sum(gains) / period if gains else 0.0
        average_loss = sum(losses) / period if losses else 0.0

        if average_loss == 0:
            return 100.0

        rs = average_gain / average_loss
        return 100 - (100 / (1 + rs))

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


class IndicatorEngine:
    """
    Calcula un set de features para el scoring (0..1) y define tendencia.
    Nota: Este engine está hecho para encajar con el score del repo.
    """

    def __init__(self, rsi_period: int = 14, atr_period: int = 14, ema_fast: int = 50, ema_slow: int = 200):
        self.rsi_period = rsi_period
        self.atr_period = atr_period
        self.ema_fast = ema_fast
        self.ema_slow = ema_slow
        logger.info("IndicatorEngine inicializado")

    @staticmethod
    def _clamp01(x: float) -> float:
        return max(0.0, min(float(x), 1.0))

    def calculate(self, candles: List[Dict[str, Any]]) -> Dict[str, Any]:
        if not candles or len(candles) < max(self.ema_slow + 5, self.atr_period + 5):
            return {
                "timeframe": "M15",
                "trend": "NEUTRAL",
                "trend_strength": 0.0,
                "rsi_component": 0.0,
                "volatility_component": 0.0,
                "momentum": 0.0,
                "structure_quality": 0.0,
                "rsi_raw": 0.0,
                "atr": 0.0,
            }

        closes = [float(c["close"]) for c in candles]
        highs = [float(c["high"]) for c in candles]
        lows = [float(c["low"]) for c in candles]

        ema_fast = Indicators.ema(closes[-(self.ema_slow + 10):], self.ema_fast)
        ema_slow = Indicators.ema(closes[-(self.ema_slow + 10):], self.ema_slow)

        if ema_fast > ema_slow:
            trend = "BUY"
        elif ema_fast < ema_slow:
            trend = "SELL"
        else:
            trend = "NEUTRAL"

        rsi_raw = Indicators.rsi(closes, self.rsi_period)
        atr_price = Indicators.atr(highs, lows, closes, self.atr_period)

        last_close = closes[-1]
        atr_safe = atr_price if atr_price > 1e-9 else max(last_close * 0.0005, 1e-6)

        # trend_strength: distancia EMAs en unidades de ATR
        trend_strength = self._clamp01(abs(ema_fast - ema_slow) / (atr_safe * 2.0))

        # rsi_component: premiar extremos claros
        if rsi_raw <= 30 or rsi_raw >= 70:
            rsi_component = 1.0
        elif rsi_raw <= 40 or rsi_raw >= 60:
            rsi_component = 0.7
        else:
            rsi_component = 0.3

        # volatility_component: ATR% preferido (simple)
        atr_pct = atr_safe / last_close if last_close else 0.0
        # preferimos ~0.3% (0.003) y penalizamos muy bajo/muy alto
        if atr_pct < 0.0008:
            volatility_component = 0.2
        elif atr_pct > 0.01:
            volatility_component = 0.3
        else:
            volatility_component = 1.0

        # momentum: retorno reciente relativo a ATR
        lookback = 10 if len(closes) > 20 else max(3, len(closes) // 5)
        ret = abs(last_close - closes[-lookback]) if len(closes) > lookback else 0.0
        momentum = self._clamp01(ret / (atr_safe * 2.0))

        # structure_quality: no perseguir precio lejos de ema_fast
        structure_quality = self._clamp01(1.0 - (abs(last_close - ema_fast) / (atr_safe * 2.5)))

        return {
            "timeframe": "M15",
            "trend": trend,
            "trend_strength": float(trend_strength),
            "rsi_component": float(rsi_component),
            "volatility_component": float(volatility_component),
            "momentum": float(momentum),
            "structure_quality": float(structure_quality),
            "rsi_raw": float(rsi_raw),
            "atr": float(atr_price),
                 }
