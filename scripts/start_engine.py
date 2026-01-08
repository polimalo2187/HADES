# scripts/start_engine.py

import signal
import sys
from core.logger import get_logger
from engine.engine_runner import EngineRunner

logger = get_logger(__name__)

engine = EngineRunner()


def shutdown_handler(sig, frame):
    logger.info("🛑 Señal de apagado recibida, deteniendo HADES Engine...")
    engine.stop()
    sys.exit(0)


def main():
    logger.info("🚀 Iniciando HADES Engine desde start_engine.py")

    # Capturar señales del sistema (Docker, VPS, Ctrl+C)
    signal.signal(signal.SIGINT, shutdown_handler)
    signal.signal(signal.SIGTERM, shutdown_handler)

    engine.start()


if __name__ == "__main__":
    main()
