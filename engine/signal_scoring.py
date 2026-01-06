# engine/signal_scoring.py

from core.logger import get_logger

logger = get_logger(__name__)


class SignalScoring:
    """
    Convierte indicadores técnicos en un score cuantitativo.
    El score determina si una señal es válida y su nivel de calidad.
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
        """
        Score final normalizado entre 0 y 1.
        Mientras más alto, mejor señal.
        """

        # Pesos (pueden ajustarse en el futuro)
        weight_trend = 0.30
        weight_rsi = 0.20
        weight_volatility = 0.20
        weight_momentum = 0.20
        weight_structure = 0.10

        score = (
            trend_strength * weight_trend
            + rsi * weight_rsi
            + volatility * weight_volatility
            + momentum * weight_momentum
            + structure_quality * weight_structure
        )

        # Clamp de seguridad
        score = max(0.0, min(score, 1.0))

        logger.debug(f"Score calculado: {score}")
        return score

    def classify_score(self, score: float) -> str:
        """
        Clasifica el score según nivel de plan.
        """
        if score >= 0.90:
            return "premium"
        elif score >= 0.80:
            return "plus"
        elif score >= 0.70:
            return "free"
        else:
            return "discarded"
