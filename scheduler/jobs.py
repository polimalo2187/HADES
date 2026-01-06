# scheduler/jobs.py

from core.logger import get_logger
from engine.engine_runner import run_engine
from signal_manager.signal_cleanup import cleanup_expired_signals

logger = get_logger(__name__)


def engine_job():
    """
    Job principal:
    Ejecuta el motor de análisis de mercado.
    Busca señales de alta calidad y las registra si cumplen score.
    """
    logger.info("⏳ Ejecutando motor de análisis de mercado (HADES)")
    try:
        run_engine()
        logger.info("✅ Motor ejecutado correctamente")
    except Exception as e:
        logger.error(f"❌ Error en engine_job: {e}")


def signal_cleanup_job():
    """
    Job de mantenimiento:
    Elimina señales vencidas según su vigencia.
    """
    logger.info("🧹 Ejecutando limpieza de señales vencidas")
    try:
        cleanup_expired_signals()
        logger.info("✅ Limpieza de señales completada")
    except Exception as e:
        logger.error(f"❌ Error en signal_cleanup_job: {e}")
