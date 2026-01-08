# engine/market_data.py

from core.logger import get_logger
from datetime import datetime
import MetaTrader5 as mt5
import time

logger = get_logger(__name__)


class MarketDataProvider:
    """
    Proveedor de datos de mercado basado en MT5.
    MT5 debe estar instalado y con sesión iniciada en el servidor.
    """

    TIMEFRAME_MAP = {
        "M1": mt5.TIMEFRAME_M1,
        "M5": mt5.TIMEFRAME_M5,
        "M15": mt5.TIMEFRAME_M15,
        "M30": mt5.TIMEFRAME_M30,
        "H1": mt5.TIMEFRAME_H1,
        "H4": mt5.TIMEFRAME_H4,
        "D1": mt5.TIMEFRAME_D1,
    }

    def __init__(self):
        self._connect()

    def _connect(self):
        """
        Inicializa conexión con MT5 de forma segura.
        """
        if mt5.initialize():
            logger.info("✅ MarketDataProvider conectado a MT5")
            return

        logger.warning("⚠️ MT5 no inicializado, reintentando...")
        time.sleep(2)

        if not mt5.initialize():
            logger.error("❌ No se pudo inicializar MT5")
            raise RuntimeError("MT5 no inicializado")

    def shutdown(self):
        """
        Cierra conexión con MT5.
        """
        mt5.shutdown()
        logger.info("🔌 Conexión MT5 cerrada")

    def get_supported_pairs(self):
        """
        Pares soportados por HADES.
        Deben existir en el Market Watch de MT5.
        """
        return [
            "EURUSD",
            "GBPUSD",
            "USDJPY",
            "USDCHF",
            "AUDUSD",
            "USDCAD",
            "NZDUSD",
            "XAUUSD",
        ]

    def fetch_latest_data(self, pair: str, timeframe: str = "M15", limit: int = 200):
        """
        Obtiene datos OHLC reales desde MT5.
        """

        if timeframe not in self.TIMEFRAME_MAP:
            raise ValueError(f"Timeframe no soportado: {timeframe}")

        if not mt5.symbol_select(pair, True):
            logger.warning(f"⚠️ Símbolo no disponible en MT5: {pair}")
            return []

        tf = self.TIMEFRAME_MAP[timeframe]

        rates = mt5.copy_rates_from_pos(pair, tf, 0, limit)

        if rates is None or len(rates) == 0:
            logger.warning(f"⚠️ Sin datos MT5 para {pair}")
            return []

        candles = []
        for r in rates:
            candles.append({
                "timestamp": datetime.fromtimestamp(r["time"]),
                "open": float(r["open"]),
                "high": float(r["high"]),
                "low": float(r["low"]),
                "close": float(r["close"]),
                "volume": float(r["tick_volume"]),
            })

        return candles
