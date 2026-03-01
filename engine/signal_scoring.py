# engine/signal_scoring.py

from core.logger import get_logger
from core.config import Config
from core.constants import PLAN_FREE, PLAN_PLUS, PLAN_PREMIUM

logger = get_logger(__name__)


class SignalScoring:
    """
    Convierte indicadores técnicos en un score cuantitativo.
    El score determina si una señal es válida y su nivel de calidad.

    IMPORTANTE: Este motor trabaja en escala 0..1.
    """

    def __init__(self):
        logger.info("SignalScoring inicializado")

    def calculate_score(
        self,
        trend_strength: float,
        rsi_component: float,
        volatility_component: float,
        momentum: float,
        structure_quality: float,
    ) -> float:
        """
        Score final normalizado entre 0 y 1.
        Mientras más alto, mejor señal.
        """

        # Pesos (ajustables)
        weight_trend = 0.30
        weight_rsi = 0.20
        weight_volatility = 0.20
        weight_momentum = 0.20
        weight_structure = 0.10

        score = (
            float(trend_strength) * weight_trend
            + float(rsi_component) * weight_rsi
            + float(volatility_component) * weight_volatility
            + float(momentum) * weight_momentum
            + float(structure_quality) * weight_structure
        )

        # Clamp de seguridad
        score = max(0.0, min(score, 1.0))
        logger.debug(f"Score calculado: {score}")
        return score

    @staticmethod
    def classify_plan(score: float) -> str:
        """
        Clasifica el score según nivel de plan (0..1).
        """
        if score >= 0.90:
            return PLAN_PREMIUM
        elif score >= 0.80:
            return PLAN_PLUS
        elif score >= 0.70:
            return PLAN_FREE
        else:
            return "discarded"


class SignalScorer:
    """
    Wrapper con la API usada por el EngineRunner:
    - score(indicators) -> float
    - is_tradeable(score) -> bool
    """

    def __init__(self):
        self.cfg = Config()
        self.scoring = SignalScoring()
        logger.info("SignalScorer inicializado")

    def score(self, indicators: dict) -> float:
        return self.scoring.calculate_score(
            trend_strength=indicators.get("trend_strength", 0.0),
            rsi_component=indicators.get("rsi_component", 0.0),
            volatility_component=indicators.get("volatility_component", 0.0),
            momentum=indicators.get("momentum", 0.0),
            structure_quality=indicators.get("structure_quality", 0.0),
        )

    def is_tradeable(self, score: float) -> bool:
        return float(score) >= float(self.cfg.MIN_SCORE_FREE)

    def plan_for_score(self, score: float) -> str:
        return self.scoring.classify_plan(float(score))
