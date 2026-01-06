# signal_manager/signal_classifier.py

from core.logger import get_logger
from core.config import Config
from core.constants import SIGNAL_ACTIVE
from signal_manager.signal_repository import SignalRepository

logger = get_logger(__name__)


class SignalClassifier:
    """
    Decide qué hacer con una nueva señal:
    - Guardarla
    - Reemplazar una existente
    - Descartarla
    """

    def __init__(self):
        self.repository = SignalRepository()

    def process_new_signal(self, new_signal: dict) -> bool:
        """
        Procesa una nueva señal.
        Retorna True si fue guardada o reemplazó otra.
        Retorna False si fue descartada.
        """

        plan = new_signal["plan"]
        new_score = new_signal["score"]

        # Limpiar señales vencidas antes de decidir
        self.repository.expire_old_signals()

        active_signal = self.repository.get_active_signal_by_plan(plan)

        # Caso 1: no hay señal activa
        if not active_signal:
            self.repository.save_new_signal(new_signal)
            logger.info(
                f"Nueva señal guardada (sin conflicto) | Plan: {plan}"
            )
            return True

        # Caso 2: comparar scores
        current_score = active_signal.get("score", 0)

        improvement = (new_score - current_score) / current_score

        if improvement >= Config.SIGNAL_REPLACE_THRESHOLD:
            # Reemplazar señal
            self.repository.cancel_signal(active_signal["_id"])
            self.repository.save_new_signal(new_signal)

            logger.info(
                f"Señal reemplazada | Plan: {plan} | "
                f"Score anterior: {current_score} → Nuevo: {new_score}"
            )
            return True

        # Caso 3: señal inferior
        logger.info(
            f"Señal descartada | Plan: {plan} | "
            f"Score actual: {current_score} | Nuevo: {new_score}"
        )
        return False
