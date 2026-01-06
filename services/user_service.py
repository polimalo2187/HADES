# services/user_service.py

from datetime import datetime, timedelta
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


class UserService:
    """
    Servicio de gestión de usuarios.
    Maneja registro, planes, vigencia y bloqueos.
    """

    COLLECTION_NAME = "users"

    def __init__(self):
        self.db = MongoDB.get_db()
        self.collection = self.db[self.COLLECTION_NAME]

    def register_user(self, user_id: int) -> dict:
        """
        Registra un usuario nuevo con plan Free (5 días).
        """
        existing = self.collection.find_one({"user_id": user_id})
        if existing:
            return existing

        user = {
            "user_id": user_id,
            "plan": PLAN_FREE,
            "status": USER_ACTIVE,
            "created_at": datetime.utcnow(),
            "plan_expires_at": datetime.utcnow()
            + timedelta(days=Config.PLAN_FREE_DAYS),
            "policy_violations": 0,
        }

        self.collection.insert_one(user)
        logger.info(f"Usuario registrado | ID: {user_id} | Plan: FREE")
        return user

    def get_user(self, user_id: int) -> dict | None:
        return self.collection.find_one({"user_id": user_id})

    def is_user_active(self, user: dict) -> bool:
        if user["status"] != USER_ACTIVE:
            return False

        if user["plan_expires_at"] < datetime.utcnow():
            return False

        return True

    def upgrade_plan(self, user_id: int, plan: str):
        """
        Activa manualmente Plus o Premium.
        """
        if plan not in [PLAN_PLUS, PLAN_PREMIUM]:
            raise ValueError("Plan inválido")

        expires = datetime.utcnow() + timedelta(
            days=Config.PLAN_PLUS_DAYS
            if plan == PLAN_PLUS
            else Config.PLAN_PREMIUM_DAYS
        )

        self.collection.update_one(
            {"user_id": user_id},
            {
                "$set": {
                    "plan": plan,
                    "plan_expires_at": expires,
                    "status": USER_ACTIVE,
                }
            },
        )

        logger.info(f"Plan activado | Usuario: {user_id} | Plan: {plan}")

    def block_user(self, user_id: int):
        """
        Bloquea permanentemente un usuario.
        """
        self.collection.update_one(
            {"user_id": user_id},
            {"$set": {"status": USER_BLOCKED}},
        )

        logger.warning(f"Usuario bloqueado | ID: {user_id}")

    def increment_policy_violation(self, user_id: int):
        """
        Incrementa violaciones de política y bloquea si excede el límite.
        """
        user = self.get_user(user_id)
        if not user:
            return

        violations = user.get("policy_violations", 0) + 1

        update = {"policy_violations": violations}

        if violations >= Config.MAX_POLICY_VIOLATIONS:
            update["status"] = USER_BLOCKED
            logger.warning(
                f"Usuario bloqueado por violaciones | ID: {user_id}"
            )

        self.collection.update_one(
            {"user_id": user_id},
            {"$set": update},
        )
