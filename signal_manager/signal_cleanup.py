# signal_manager/signal_cleanup.py

from core.logger import get_logger
from signal_manager.signal_repository import SignalRepository

logger = get_logger(__name__)


class SignalCleanup:
    """
    Limpieza programada de señales.
    Se ejecuta mediante scheduler.
    """

    def __init__(self):
        self.repository = SignalRepository()

    def run(self):
        """
        Ejecuta la limpieza de señales vencidas.
        """
        logger.info("Ejecutando limpieza de señales vencidas")
        self.repository.expire_old_signals()
