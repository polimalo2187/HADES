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

    Regla: el usuario SOLO ve señales del plan exacto que tiene.
    """

    def __init__(self):
        self.signal_repository = SignalRepository()
        self.user_service = UserService()

    def get_signal_for_user(self, user_id: int) -> dict | None:
        user = self.user_service.get_user(int(user_id))
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
# WRAPPER (compatibilidad con telegram_bot/handlers/signals.py)
# ─────────────────────────────────────────────────────────────

_signal_service = SignalService()


def get_active_signal_for_user(user_id: int, plan: str | None = None) -> dict | None:
    """
    Handler llama: get_active_signal_for_user(user_id, plan)
    Por seguridad usamos el plan real del usuario (plan exacto).
    """
    return _signal_service.get_signal_for_user(int(user_id))
