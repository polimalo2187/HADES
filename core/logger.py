# core/logger.py

import logging
import os

LOG_LEVEL = logging.INFO
LOG_FORMAT = "%(asctime)s | %(levelname)s | %(name)s | %(message)s"
LOG_DIR = "logs"

os.makedirs(LOG_DIR, exist_ok=True)


def get_logger(name: str) -> logging.Logger:
    logger = logging.getLogger(name)
    logger.setLevel(LOG_LEVEL)

    if not logger.handlers:
        formatter = logging.Formatter(LOG_FORMAT)

        # Consola
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)

        # Archivo
        file_handler = logging.FileHandler(f"{LOG_DIR}/hades.log")
        file_handler.setFormatter(formatter)

        logger.addHandler(console_handler)
        logger.addHandler(file_handler)

    return logger
