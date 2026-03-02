# engine/market_data.py

from core.logger import get_logger
from core.config import settings
from datetime import datetime
import MetaTrader5 as mt5
import time
import re
import os
import glob
from typing import Optional

logger = get_logger(__name__)


class MarketDataProvider:
    """
    Proveedor de datos de mercado basado en MT5 (Windows).

    ✅ Modo Producción (24/7, sin depender de que tú abras MT5):
    - Si defines MT5_TERMINAL_PATH, MarketDataProvider intentará inicializar MT5 apuntando al terminal
      (MT5 se levanta automáticamente si no está corriendo).
    - Si defines MT5_LOGIN / MT5_PASSWORD / MT5_SERVER, intentará hacer login automáticamente.
    - Si NO defines credenciales, funciona con la sesión que ya tengas abierta dentro de MT5.

    Variables nuevas (opcionales, pero recomendadas):
      - MT5_TERMINAL_PATH   -> ruta a terminal64.exe
      - MT5_LOGIN           -> número de cuenta
      - MT5_PASSWORD        -> contraseña
      - MT5_SERVER          -> ej: HantecMarketsV-LIVE
      - MT5_INIT_RETRIES    -> default 15
      - MT5_RETRY_SLEEP_SEC -> default 2
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

    # -----------------------------
    # Conexión / Auto-login
    # -----------------------------
    @staticmethod
    def _find_terminal_path() -> Optional[str]:
        """
        Intenta localizar terminal64.exe automáticamente en rutas típicas de Windows.
        Esto te evita tener que saber la carpeta exacta.
        """
        # 1) env explícito
        explicit = getattr(settings, "MT5_TERMINAL_PATH", "") or os.getenv("MT5_TERMINAL_PATH", "")
        explicit = (explicit or "").strip().strip('"')
        if explicit:
            if os.path.isfile(explicit):
                return explicit
            logger.warning(f"⚠️ MT5_TERMINAL_PATH definido pero no existe: {explicit}")

        # 2) búsquedas típicas (Program Files / Program Files (x86) / LocalAppData)
        candidates = []
        pf = os.environ.get("ProgramFiles", r"C:\Program Files")
        pfx86 = os.environ.get("ProgramFiles(x86)", r"C:\Program Files (x86)")
        local = os.environ.get("LOCALAPPDATA", "")

        search_roots = [pf, pfx86]
        if local:
            search_roots.append(local)

        patterns = [
            "**\\terminal64.exe",
            "**\\terminal.exe",
        ]

        for root in search_roots:
            if not root or not os.path.isdir(root):
                continue
            for pat in patterns:
                matches = glob.glob(os.path.join(root, pat), recursive=True)
                for m in matches:
                    # Preferimos instalaciones relacionadas a MetaTrader / MT5 / Hantec
                    lm = m.lower()
                    if any(k in lm for k in ["metatrader", "mt5", "hantec", "hmarkets"]):
                        candidates.append(m)
                    else:
                        candidates.append(m)

        # heurística: primero los que parecen MT5
        def score(p: str) -> int:
            lp = p.lower()
            s = 0
            for k, w in [
                ("terminal64.exe", 10),
                ("mt5", 8),
                ("metatrader", 6),
                ("hantec", 6),
                ("hmarkets", 6),
                ("program files", 2),
            ]:
                if k in lp:
                    s += w
            return s

        candidates = sorted(set(candidates), key=score, reverse=True)
        return candidates[0] if candidates else None

    @staticmethod
    def _try_login() -> bool:
        """
        Intenta login si existen MT5_LOGIN/MT5_PASSWORD/MT5_SERVER.
        Si no existen, retorna True (asumimos sesión manual).
        """
        login_raw = (getattr(settings, "MT5_LOGIN", "") or os.getenv("MT5_LOGIN", "")).strip()
        password = (getattr(settings, "MT5_PASSWORD", "") or os.getenv("MT5_PASSWORD", "")).strip()
        server = (getattr(settings, "MT5_SERVER", "") or os.getenv("MT5_SERVER", "")).strip()

        if not login_raw and not password and not server:
            # sesión ya abierta en MT5
            return True

        if not (login_raw and password and server):
            logger.error(
                "❌ Config MT5 incompleta. Para auto-login define MT5_LOGIN, MT5_PASSWORD y MT5_SERVER. "
                "O deja los 3 vacíos para usar la sesión ya abierta."
            )
            return False

        try:
            login = int(login_raw)
        except Exception:
            logger.error("❌ MT5_LOGIN debe ser numérico (login de MT5, no correo).")
            return False

        ok = mt5.login(login=login, password=password, server=server)
        if ok:
            logger.info(f"✅ Login MT5 OK en {server} (login {login})")
            return True

        last_error = mt5.last_error()
        logger.error(f"❌ Login MT5 falló. last_error={last_error}")
        return False

    def _connect(self):
        """
        Inicializa conexión con MT5 de forma robusta (24/7).
        """
        retries = int(getattr(settings, "MT5_INIT_RETRIES", os.getenv("MT5_INIT_RETRIES", "15")))
        sleep_sec = float(getattr(settings, "MT5_RETRY_SLEEP_SEC", os.getenv("MT5_RETRY_SLEEP_SEC", "2")))

        terminal_path = self._find_terminal_path()
        if terminal_path:
            logger.info(f"🧩 Usando terminal MT5: {terminal_path}")
        else:
            logger.warning(
                "⚠️ No pude encontrar terminal64.exe automáticamente. "
                "Si falla la inicialización, define MT5_TERMINAL_PATH."
            )

        # Intentar inicialización con y sin path
        for attempt in range(1, retries + 1):
            try:
                if terminal_path:
                    ok_init = mt5.initialize(path=terminal_path)
                else:
                    ok_init = mt5.initialize()
            except Exception as e:
                ok_init = False
                logger.warning(f"⚠️ Excepción inicializando MT5 (intento {attempt}/{retries}): {e}")

            if ok_init:
                # Auto-login si hay credenciales
                if self._try_login():
                    logger.info("✅ MarketDataProvider conectado a MT5")
                    return

                # login falló: cerramos y reintentamos
                mt5.shutdown()
                time.sleep(sleep_sec)
                continue

            # init falló: log + retry
            last_error = mt5.last_error()
            logger.warning(f"⚠️ MT5 no inicializado (intento {attempt}/{retries}). last_error={last_error}")
            time.sleep(sleep_sec)

        raise RuntimeError(
            "MT5 no inicializado. Revisa que MT5 esté instalado en el VPS Windows, "
            "y/o define MT5_TERMINAL_PATH. Si usas auto-login, define MT5_LOGIN/MT5_PASSWORD/MT5_SERVER."
        )

    def shutdown(self):
        """
        Cierra conexión con MT5.
        """
        try:
            mt5.shutdown()
        finally:
            logger.info("🔌 Conexión MT5 cerrada")

    # -----------------------------
    # Símbolos y datos
    # -----------------------------
    @staticmethod
    def _normalize_symbol(name: str) -> str:
        # Many brokers use suffixes like EURUSD.m / EURUSD_i / EURUSDpro
        return re.sub(r"[^A-Z]", "", (name or "").upper())

    def get_symbol_info(self, symbol: str):
        return mt5.symbol_info(symbol)

    def get_forex_pairs(self):
        """
        Devuelve todos los símbolos que parecen pares FX (EURUSD, GBPJPY, etc.)
        disponibles en el broker (según symbols_get()).
        """
        symbols = mt5.symbols_get()
        out = []
        if not symbols:
            return out

        for s in symbols:
            name = s.name
            norm = self._normalize_symbol(name)
            if len(norm) != 6:
                continue
            out.append(name)

        # Seleccionar en MarketWatch para poder obtener rates
        for name in out:
            mt5.symbol_select(name, True)

        return out

    def get_supported_pairs(self):
        """
        Mantiene compatibilidad: ahora devuelve todos los pares FX disponibles.
        """
        return self.get_forex_pairs()

    def fetch_latest_data(self, pair: str, timeframe: str = "M15", limit: int = 200):
        """
        Obtiene datos OHLC reales desde MT5.
        Retorna una lista de velas (dicts) con volume=tick_volume.
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
            candles.append(
                {
                    "timestamp": datetime.fromtimestamp(r["time"]),
                    "open": float(r["open"]),
                    "high": float(r["high"]),
                    "low": float(r["low"]),
                    "close": float(r["close"]),
                    "volume": float(r["tick_volume"]),
                }
            )

        return candles
