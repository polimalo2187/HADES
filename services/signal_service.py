# services/signal_service.py

from __future__ import annotations

from core.logger import get_logger
from core.constants import SIGNAL_ACTIVE
from signal_manager.signal_repository import SignalRepository
from services.user_service import UserService

logger = get_logger(__name__)


class SignalService:
    """
    Servicio que entrega señales a los usuarios según su plan y estado.
    """

    def __init__(self):
        self.signal_repository = SignalRepository()
        self.user_service = UserService()

    def get_signal_for_user(self, user_id: int) -> dict | None:
        user = self.user_service.get_user(user_id)
        if not user:
            logger.warning(f"Usuario no registrado solicitó señal | ID: {user_id}")
            return None

        if not self.user_service.is_user_active(user):
            logger.info(f"Usuario sin acceso a señales | ID: {user_id}")
            return None

        plan = user.get("plan")
        signal = self.signal_repository.get_active_signal_by_plan(plan)

        if not signal or signal.get("status") != SIGNAL_ACTIVE:
            return None

        return signal


# ─────────────────────────────────────────────────────────────
# WRAPPER + ADAPTADOR PARA TELEGRAM
# ─────────────────────────────────────────────────────────────

_signal_service_singleton = SignalService()


def _expand_signal_for_telegram(signal: dict) -> dict:
    """
    Telegram espera:
      tp_conservative/sl_conservative, tp_moderate/sl_moderate, tp_aggressive/sl_aggressive,
      estimated_time, signal_id
    Pero el engine normalmente guarda: id, entry, tp, sl, direction, pair, timeframe, plan...

    Aquí adaptamos sin tocar los handlers.
    """
    if not signal:
        return signal

    # Copia defensiva
    s = dict(signal)

    entry = float(s.get("entry", 0.0) or 0.0)
    tp = float(s.get("tp", 0.0) or 0.0)
    sl = float(s.get("sl", 0.0) or 0.0)
    direction = str(s.get("direction", "")).upper()

    # Distancia de riesgo basada en SL
    risk = abs(entry - sl)
    if risk <= 0:
        # fallback: si no hay SL válido, inventa una distancia mínima relativa
        risk = max(entry * 0.001, 0.0001)

    # Tres perfiles: conservador/moderado/agresivo (mismo SL, TP distinto)
    rr_conservative = 1.5
    rr_moderate = 2.5
    rr_aggressive = 4.0

    if direction == "SELL":
        tp_cons = entry - rr_conservative * risk
        tp_mod = entry - rr_moderate * risk
        tp_aggr = entry - rr_aggressive * risk
    else:  # BUY o desconocido -> BUY
        tp_cons = entry + rr_conservative * risk
        tp_mod = entry + rr_moderate * risk
        tp_aggr = entry + rr_aggressive * risk

    # SL por perfil (igual para no romper lógica)
    s["tp_conservative"] = round(tp_cons, 5)
    s["sl_conservative"] = round(sl, 5)
    s["tp_moderate"] = round(tp_mod, 5)
    s["sl_moderate"] = round(sl, 5)
    s["tp_aggressive"] = round(tp_aggr, 5)
    s["sl_aggressive"] = round(sl, 5)

    # estimated_time (heurística simple por TF)
    tf = str(s.get("timeframe", "M15")).upper()
    est_map = {
        "M5": "30–90 min",
        "M15": "1–4 h",
        "M30": "2–6 h",
        "H1": "4–12 h",
        "H4": "12–48 h",
        "D1": "2–7 días",
    }
    s["estimated_time"] = est_map.get(tf, "1–6 h")

    # alias para handler
    s["signal_id"] = s.get("id", "")

    return s


def get_active_signal_for_user(user_id: int, plan: str | None = None) -> dict | None:
    """
    Usado por telegram_bot/handlers/signals.py

    Nota:
    - El handler pasa (user_id, plan), pero aquí el plan real lo tomamos del usuario
      para evitar inconsistencias.
    """
    signal = _signal_service_singleton.get_signal_for_user(int(user_id))
    if not signal:
        return None
    return _expand_signal_for_telegram(signal)
