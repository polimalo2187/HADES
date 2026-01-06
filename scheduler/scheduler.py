# scheduler/scheduler.py

from apscheduler.schedulers.background import BackgroundScheduler
from core.logger import get_logger

logger = get_logger(__name__)


class SchedulerManager:
    """
    Administrador central del scheduler del sistema.
    Ejecuta tareas del motor de análisis y mantenimiento
    de forma independiente a Telegram.
    """

    def __init__(self):
        self.scheduler = BackgroundScheduler(timezone="UTC")

    def add_job(self, func, trigger, **kwargs):
        """
        Agrega un job al scheduler.
        """
        self.scheduler.add_job(func, trigger, **kwargs)
        logger.info(f"Job agregado: {func.__name__}")

    def start(self):
        """
        Inicia el scheduler.
        """
        self.scheduler.start()
        logger.info("Scheduler iniciado correctamente")

    def shutdown(self):
        """
        Detiene el scheduler de forma segura.
        """
        self.scheduler.shutdown(wait=False)
        logger.info("Scheduler detenido")
