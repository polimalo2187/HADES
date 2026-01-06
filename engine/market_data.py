# engine/market_data.py

from core.logger import get_logger

logger = get_logger(__name__)


class MarketDataProvider:
    """
    Proveedor abstracto de datos de mercado.
    Este módulo NO depende de ningún broker.
    """

    def __init__(self):
        logger.info("MarketDataProvider inicializado")

    def get_supported_pairs(self):
        """
        Devuelve la lista de pares que HADES puede analizar.
        Inicialmente trabajaremos solo con los pares más líquidos.
        """
        return [
            "EURUSD",
            "GBPUSD",
            "USDJPY",
            "USDCHF",
            "AUDUSD",
            "USDCAD",
            "NZDUSD",
        ]

    def fetch_latest_data(self, pair: str, timeframe: str = "M15", limit: int = 200):
        """
        Obtiene datos OHLC del mercado general.
        Este método será implementado con la fuente de datos elegida
        (agregadores de mercado, feeds institucionales, etc.).

        Retorna una lista de velas con:
        {
            'timestamp': datetime,
            'open': float,
            'high': float,
            'low': float,
            'close': float,
            'volume': float
        }
        """

        logger.debug(f"Solicitando datos de mercado para {pair} ({timeframe})")

        # Placeholder: aún no conectamos la fuente real
        return []
