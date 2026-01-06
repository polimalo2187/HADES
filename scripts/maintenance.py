# scripts/maintenance.py

from core.logger import get_logger
from signal_manager.signal_cleanup import cleanup_expired_signals
from services.security_service import cleanup_blocked_users

logger = get_logger(__name__)


def main():
    logger.info("🧹 Ejecutando mantenimiento del sistema")

    cleanup_expired_signals()
    cleanup_blocked_users()

    logger.info("✅ Mantenimiento completado")


if __name__ == "__main__":
    main()
