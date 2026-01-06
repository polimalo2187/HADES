# scripts/start_engine.py

from core.logger import get_logger
from engine.engine_runner import run_engine

logger = get_logger(__name__)


def main():
    logger.info("🔥 Iniciando Engine de Análisis HADES")
    run_engine()


if __name__ == "__main__":
    main()
