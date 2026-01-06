# core/config.py

import os
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()


class Config:
    # ===============================
    # PROYECTO
    # ===============================
    PROJECT_NAME = "HADES"
    ENVIRONMENT = os.getenv("ENVIRONMENT", "production")

    # ===============================
    # MONGODB
    # ===============================
    MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017")
    MONGO_DB_NAME = os.getenv("MONGO_DB_NAME", "hades_db")

    # ===============================
    # TELEGRAM
    # ===============================
    TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "")
    TELEGRAM_ADMIN_IDS = [
        int(admin_id)
        for admin_id in os.getenv("TELEGRAM_ADMIN_IDS", "").split(",")
        if admin_id.strip().isdigit()
    ]

    # ===============================
    # PLANES (DURACIÓN EN DÍAS)
    # ===============================
    PLAN_FREE_DAYS = 5
    PLAN_PLUS_DAYS = 30
    PLAN_PREMIUM_DAYS = 30

    # ===============================
    # SEÑALES
    # ===============================
    SIGNAL_EXPIRATION_HOURS = 24  # vigencia máxima de una señal
    SIGNAL_REPLACE_THRESHOLD = 0.10  # 10% mejor score para reemplazar

    # ===============================
    # SEGURIDAD
    # ===============================
    MAX_POLICY_VIOLATIONS = 1
