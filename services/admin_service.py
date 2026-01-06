# services/admin_service.py

from core.database import MongoDB
from core.logger import get_logger
from core.config import Config
from core.constants import (
    PLAN_FREE,
    PLAN_PLUS,
    PLAN_PREMIUM,
    USER_ACTIVE,
    USER_BLOCKED,
)

logger = get_logger(__name__)


class AdminService:
    """
    Servicio de administración.
    Control total del sistema HADES por parte de administradores.
    """

    COLLECTION_NAME = "users"

    def __init__(self):
        self.db = MongoDB.get_db()
        self.collection = self.db[self.COLLECTION_NAME]

    def is_admin(self, user_id: int) -> bool:
        """
        Verifica si un usuario es administrador.
        """
        return user_id in Config.TELEGRAM_ADMIN_IDS

    def get_user_statistics(self) -> dict:
        """
        Retorna estadísticas globales de usuarios.
        """
        total = self.collection.count_documents({})

        free = self.collection.count_documents({"plan": PLAN_FREE})
        plus = self.collection.count_documents({"plan": PLAN_PLUS})
        premium = self.collection.count_documents({"plan": PLAN_PREMIUM})

        active = self.collection.count_documents({"status": USER_ACTIVE})
        blocked = self.collection.count_documents({"status": USER_BLOCKED})

        stats = {
            "total_users": total,
            "free": free,
            "plus": plus,
            "premium": premium,
            "active": active,
            "blocked": blocked,
        }

        logger.info("Estadísticas de usuarios solicitadas por admin")
        return stats

    def get_user_by_id(self, user_id: int) -> dict | None:
        """
        Obtiene información detallada de un usuario por ID.
        """
        return self.collection.find_one({"user_id": user_id})
