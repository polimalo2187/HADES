# services/user_service.py

from __future__ import annotations

from datetime import datetime, timedelta
from typing import Optional

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

    def register_user(self, user_id: int, username: Optional[str] = None, telegram_chat_id: Optional[int] = None) -> dict:
        """
        Registra un usuario nuevo con plan Free.
        Si ya existe, actualiza metadata básica (username/chat_id) si viene.
        """
        existing = self.collection.find_one({"user_id": user_id})
        if existing:
            update = {}
            if username and existing.get("username") != username:
                update["username"] = username
            if telegram_chat_id and existing.get("telegram_chat_id") != telegram_chat_id:
                update["telegram_chat_id"] = telegram_chat_id
            if update:
                self.collection.update_one({"user_id": user_id}, {"$set": update})
                existing.update(update)
            return existing

        user = {
            "user_id": int(user_id),
            "username": username,
            "telegram_chat_id": telegram_chat_id,
            "plan": PLAN_FREE,
            "status": USER_ACTIVE,
            "created_at": datetime.utcnow(),
            "plan_expires_at": datetime.utcnow() + timedelta(days=Config.PLAN_FREE_DAYS),
            "policy_violations": 0,
            # preparado para push (más adelante)
            "push_enabled": True,
        }

        self.collection.insert_one(user)
        logger.info(f"Usuario registrado | ID: {user_id} | Plan: FREE")
        return user

    def get_user(self, user_id: int) -> Optional[dict]:
        return self.collection.find_one({"user_id": int(user_id)})

    def is_user_active(self, user: dict) -> bool:
        if not user:
            return False
        if user.get("status") != USER_ACTIVE:
            return False
        if user.get("plan_expires_at") and user["plan_expires_at"] < datetime.utcnow():
            return False
        return True

    def get_user_plan(self, user_id: int) -> str:
        user = self.get_user(user_id)
        if not user:
            # auto-registro defensivo
            user = self.register_user(user_id=user_id)
        return user.get("plan", PLAN_FREE)

    def is_plan_active(self, user_id: int) -> bool:
        user = self.get_user(user_id)
        if not user:
            return False
        return self.is_user_active(user)

    def upgrade_plan(self, user_id: int, plan: str) -> bool:
        """
        Activa manualmente Plus o Premium.
        """
        if plan not in [PLAN_PLUS, PLAN_PREMIUM]:
            raise ValueError("Plan inválido")

        expires = datetime.utcnow() + timedelta(
            days=Config.PLAN_PLUS_DAYS if plan == PLAN_PLUS else Config.PLAN_PREMIUM_DAYS
        )

        self.collection.update_one(
            {"user_id": int(user_id)},
            {"$set": {"plan": plan, "plan_expires_at": expires, "status": USER_ACTIVE}},
            upsert=True,
        )
        logger.info(f"Plan activado | Usuario: {user_id} | Plan: {plan}")
        return True

    def block_user(self, user_id: int) -> bool:
        """
        Bloquea permanentemente un usuario.
        """
        res = self.collection.update_one(
            {"user_id": int(user_id)},
            {"$set": {"status": USER_BLOCKED}},
            upsert=False,
        )
        if res.matched_count == 0:
            return False
        logger.warning(f"Usuario bloqueado | ID: {user_id}")
        return True

    def increment_policy_violation(self, user_id: int) -> None:
        """
        Incrementa violaciones de política y bloquea si excede el límite.
        """
        user = self.get_user(user_id)
        if not user:
            return

        violations = int(user.get("policy_violations", 0)) + 1
        update = {"policy_violations": violations}

        if violations >= int(Config.MAX_POLICY_VIOLATIONS):
            update["status"] = USER_BLOCKED
            logger.warning(f"Usuario bloqueado por violaciones | ID: {user_id}")

        self.collection.update_one({"user_id": int(user_id)}, {"$set": update})


# ─────────────────────────────────────────────────────────────
# WRAPPERS (compatibilidad con handlers que importan funciones)
# ─────────────────────────────────────────────────────────────

_user_service_singleton = UserService()


def register_user_if_not_exists(telegram_id: int, username: Optional[str] = None) -> dict:
    """
    Usado por telegram_bot/handlers/start.py
    """
    return _user_service_singleton.register_user(user_id=int(telegram_id), username=username, telegram_chat_id=int(telegram_id))


def get_user_plan(user_id: int) -> str:
    """
    Usado por telegram_bot/handlers/signals.py
    """
    return _user_service_singleton.get_user_plan(int(user_id))


def is_plan_active(user_id: int) -> bool:
    """
    Usado por telegram_bot/handlers/signals.py
    """
    return _user_service_singleton.is_plan_active(int(user_id))


def activate_user_plan(user_id: int, plan: str) -> bool:
    """
    Usado por admin handlers (activar plan)
    """
    return _user_service_singleton.upgrade_plan(int(user_id), plan)


def block_user_by_id(user_id: int) -> bool:
    """
    Usado por admin handlers (bloquear)
    """
    return _user_service_singleton.block_user(int(user_id))


def get_users_statistics() -> dict:
    """
    Usado por telegram_bot/handlers/admin/user_info.py
    Este wrapper delega en AdminService para devolver llaves esperadas.
    """
    from services.admin_service import AdminService  # import local para evitar ciclos

    stats = AdminService().get_user_statistics()
    # handler espera: total/free/plus/premium
    return {
        "total": stats.get("total_users", 0),
        "free": stats.get("free", 0),
        "plus": stats.get("plus", 0),
        "premium": stats.get("premium", 0),
      }
