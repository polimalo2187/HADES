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
        logger.info("Ejecutando limpieza de señales vencidas")
        self.repository.expire_old_signals()

    # Compatibilidad con engine_runner
    def cleanup_expired_signals(self):
        self.run()


# ─────────────────────────────────────────────────────────────
# WRAPPER para scheduler/scripts
# ─────────────────────────────────────────────────────────────

_cleanup_singleton = SignalCleanup()


def cleanup_expired_signals():
    """
    Usado por scheduler/jobs.py y scripts/maintenance.py
    """
    return _cleanup_singleton.run()
