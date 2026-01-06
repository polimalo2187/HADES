# engine/engine_runner.py

import time
from core.logger import get_logger

logger = get_logger(__name__)


class EngineRunner:
    """
    Ejecuta el motor de análisis de mercado 24/7.
    No depende de Telegram.
    """

    def __init__(self, interval_seconds: int = 60):
        self.interval_seconds = interval_seconds
        self.running = False

    def start(self):
        logger.info("HADES Engine iniciado (modo 24/7)")
        self.running = True

        while self.running:
            try:
                self.run_cycle()
            except Exception as e:
                logger.error(f"Error en ciclo del engine: {e}")

            time.sleep(self.interval_seconds)

    def stop(self):
        self.running = False
        logger.info("HADES Engine detenido")

    def run_cycle(self):
        """
        Un ciclo completo de análisis.
        Aquí luego se conectarán:
        - market_data
        - indicators
        - signal_scoring
        - signal_generator
        """
        logger.info("Ejecutando ciclo de análisis de mercado")
