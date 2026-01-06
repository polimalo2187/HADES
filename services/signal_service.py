# services/signal_service.py

from core.logger import get_logger
from core.constants import SIGNAL_ACTIVE
from signal_manager.signal_repository import SignalRepository
from services.user_service import UserService

logger = get_logger(__name__)


class SignalService:
    """
    Servicio que entrega señales a los usuarios
    según su plan y estado.
    """

    def __init__(self):
        self.signal_repository = SignalRepository()
        self.user_service = UserService()

    def get_signal_for_user(self, user_id: int) -> dict | None:
        """
        Retorna la señal correspondiente al plan del usuario.
        Si no hay señal o el usuario no tiene acceso, retorna None.
        """

        user = self.user_service.get_user(user_id)
        if not user:
            logger.warning(f"Usuario no registrado solicitó señal | ID: {user_id}")
            return None

        if not self.user_service.is_user_active(user):
            logger.info(f"Usuario sin acceso a señales | ID: {user_id}")
            return None

        plan = user["plan"]

        signal = self.signal_repository.get_active_signal_by_plan(plan)
        if not signal or signal.get("status") != SIGNAL_ACTIVE:
            return None

        return signal
