# scheduler/jobs.py

from core.logger import get_logger
from engine.engine_runner import run_engine
from signal_manager.signal_cleanup import cleanup_expired_signals
from services.push_notifications_service import PushNotificationsService

logger = get_logger(__name__)


def engine_job():
    """
    Ejecuta 1 ciclo del motor.
    """
    logger.info("⏳ Ejecutando motor de análisis de mercado (HADES)")
    try:
        run_engine()
        logger.info("✅ Motor ejecutado correctamente")
    except Exception as e:
        logger.exception(f"❌ Error en engine_job: {e}")


def signal_cleanup_job():
    """
    Limpia señales vencidas.
    """
    logger.info("🧹 Ejecutando limpieza de señales vencidas")
    try:
        cleanup_expired_signals()
        logger.info("✅ Limpieza de señales completada")
    except Exception as e:
        logger.exception(f"❌ Error en signal_cleanup_job: {e}")


def push_notifications_job():
    """
    Envía push (sin señal) por plan exacto.
    """
    try:
        stats = PushNotificationsService().run()
        logger.info(
            "🔔 Push job stats | sent=%s failed=%s dup=%s no_chat=%s inactive=%s plans=%s",
            stats.get("sent"),
            stats.get("failed"),
            stats.get("skipped_duplicate"),
            stats.get("skipped_no_chat_id"),
            stats.get("skipped_inactive"),
            stats.get("plans"),
        )
    except Exception as e:
        logger.exception(f"❌ Error en push_notifications_job: {e}")
