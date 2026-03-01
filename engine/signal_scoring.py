# engine/signal_scoring.py

from core.logger import get_logger

logger = get_logger(__name__)


class SignalScoring:
    """
    Convierte indicadores técnicos en un score cuantitativo.
    Score en escala 0..1.
    """

    def __init__(self):
        logger.info("SignalScoring inicializado")

    def calculate_score(
        self,
        trend_strength: float,
        rsi: float,
        volatility: float,
        momentum: float,
        structure_quality: float,
    ) -> float:
        # Pesos
        weight_trend = 0.30
        weight_rsi = 0.20
        weight_volatility = 0.20
        weight_momentum = 0.20
        weight_structure = 0.10

        score = (
            float(trend_strength) * weight_trend
            + float(rsi) * weight_rsi
            + float(volatility) * weight_volatility
            + float(momentum) * weight_momentum
            + float(structure_quality) * weight_structure
        )

        return max(0.0, min(float(score), 1.0))

    def classify_score(self, score: float) -> str:
        if score >= 0.90:
            return "premium"
        elif score >= 0.80:
            return "plus"
        elif score >= 0.70:
            return "free"
        return "discarded"


class SignalScorer:
    """
    API que usa engine/engine_runner.py:
      - score(indicators) -> float
      - is_tradeable(score) -> bool
    """

    def __init__(self):
        self.scoring = SignalScoring()
        logger.info("SignalScorer inicializado")

    def score(self, indicators: dict) -> float:
        return self.scoring.calculate_score(
            trend_strength=indicators.get("trend_strength", 0.0),
            rsi=indicators.get("rsi_component", 0.0),
            volatility=indicators.get("volatility_component", 0.0),
            momentum=indicators.get("momentum", 0.0),
            structure_quality=indicators.get("structure_quality", 0.0),
        )

    def is_tradeable(self, score: float) -> bool:
        # mínimo base para “free”
        return float(score) >= 0.70
