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
    # MT5 / BROKER (Windows VPS)
    # ===============================
    # Para 24/7 sin depender de abrir MT5 manualmente, define:
    #   MT5_LOGIN, MT5_PASSWORD, MT5_SERVER, (opcional) MT5_TERMINAL_PATH
    #
    # Si NO defines estas variables, HADES usará la sesión que ya esté abierta en MT5.
    MT5_LOGIN = os.getenv("MT5_LOGIN", "")
    MT5_PASSWORD = os.getenv("MT5_PASSWORD", "")
    MT5_SERVER = os.getenv("MT5_SERVER", "")
    MT5_TERMINAL_PATH = os.getenv("MT5_TERMINAL_PATH", "")

    # Reintentos para inicializar/login
    MT5_INIT_RETRIES = int(os.getenv("MT5_INIT_RETRIES", "15"))
    MT5_RETRY_SLEEP_SEC = float(os.getenv("MT5_RETRY_SLEEP_SEC", "2"))

    # ===============================
    # PLANES (DURACIÓN EN DÍAS)
    # ===============================
    PLAN_FREE_DAYS = int(os.getenv("PLAN_FREE_DAYS", "5"))
    PLAN_PLUS_DAYS = int(os.getenv("PLAN_PLUS_DAYS", "30"))
    PLAN_PREMIUM_DAYS = int(os.getenv("PLAN_PREMIUM_DAYS", "30"))

    # ===============================
    # SEÑALES
    # ===============================
    SIGNAL_EXPIRATION_HOURS = int(os.getenv("SIGNAL_EXPIRATION_HOURS", "24"))  # vigencia máxima de una señal
    SIGNAL_REPLACE_THRESHOLD = float(os.getenv("SIGNAL_REPLACE_THRESHOLD", "0.10"))  # 10% mejor score para reemplazar

    # ===============================
    # MOTOR: MODO ALTA EFECTIVIDAD (H1 + filtro H4)
    # ===============================
    TIMEFRAME_SIGNAL = os.getenv("TIMEFRAME_SIGNAL", "H1")
    TIMEFRAME_TREND = os.getenv("TIMEFRAME_TREND", "H4")
    BAR_CLOSE_ONLY = os.getenv("BAR_CLOSE_ONLY", "true").lower() in ("1", "true", "yes", "y")

    # Universo (liquidez)
    LIQUIDITY_BARS = int(os.getenv("LIQUIDITY_BARS", "500"))          # velas para estimar tick_volume (H1)
    LIQUIDITY_TOP_PCT = float(os.getenv("LIQUIDITY_TOP_PCT", "0.60")) # top 60% por tick_volume mediano

    # Spread vs ATR
    ATR_PERIOD = int(os.getenv("ATR_PERIOD", "14"))
    MAX_SPREAD_ATR_RATIO = float(os.getenv("MAX_SPREAD_ATR_RATIO", "0.15"))  # spread <= 15% de ATR (en puntos)

    # Señal (umbrales score 0..1)
    COOLDOWN_BARS = int(os.getenv("COOLDOWN_BARS", "2"))  # velas de cooldown por símbolo
    MIN_SCORE_FREE = float(os.getenv("MIN_SCORE_FREE", "0.70"))
    MIN_SCORE_PLUS = float(os.getenv("MIN_SCORE_PLUS", "0.80"))
    MIN_SCORE_PREMIUM = float(os.getenv("MIN_SCORE_PREMIUM", "0.90"))

    # ===============================
    # SEGURIDAD
    # ===============================
    MAX_POLICY_VIOLATIONS = int(os.getenv("MAX_POLICY_VIOLATIONS", "1"))


# Alias compatible con el código existente del bot de Telegram
settings = Config()
