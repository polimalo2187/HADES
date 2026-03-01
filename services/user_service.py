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

    Nota:
    - Guardamos telegram_chat_id para push.
    - Guardamos username (opcional).
    - Guardamos push_enabled y last_notified_signal_id (para deduplicación).
    """

    COLLECTION_NAME = "users"

    def __init__(self):
        self.db = MongoDB.get_db()
        self.collection = self.db[self.COLLECTION_NAME]

    def register_user(
        self,
        user_id: int,
        username: Optional[str] = None,
        telegram_chat_id: Optional[int] = None,
    ) -> dict:
        """
        Registra un usuario nuevo con plan Free (Config.PLAN_FREE_DAYS).
        Si ya existe, actualiza username/chat_id si vienen.
        """
        user_id = int(user_id)
        existing = self.collection.find_one({"user_id": user_id})
        if existing:
            update = {}
            if username is not None and existing.get("username") != username:
                update["username"] = username
            if telegram_chat_id is not None and existing.get("telegram_chat_id") != int(telegram_chat_id):
                update["telegram_chat_id"] = int(telegram_chat_id)
            # Asegurar campos para push/dedup sin romper usuarios viejos
            if "push_enabled" not in existing:
                update["push_enabled"] = True
            if "last_notified_signal_id" not in existing:
                update["last_notified_signal_id"] = None

            if update:
                self.collection.update_one({"user_id": user_id}, {"$set": update})
                existing.update(update)

            return existing

        user = {
            "user_id": user_id,
            "username": username,
            "telegram_chat_id": int(telegram_chat_id) if telegram_chat_id is not None else None,
            "plan": PLAN_FREE,
            "status": USER_ACTIVE,
            "created_at": datetime.utcnow(),
            "plan_expires_at": datetime.utcnow() + timedelta(days=Config.PLAN_FREE_DAYS),
            "policy_violations": 0,
            # Push / dedup
            "push_enabled": True,
            "last_notified_signal_id": None,
        }

        self.collection.insert_one(user)
        logger.info(f"Usuario registrado | ID: {user_id} | Plan: FREE")
        return user

    def get_user(self, user_id: int) -> dict | None:
        return self.collection.find_one({"user_id": int(user_id)})

    def is_user_active(self, user: dict) -> bool:
        if not user:
            return False

        if user.get("status") != USER_ACTIVE:
            return False

        expires = user.get("plan_expires_at")
        if expires and expires < datetime.utcnow():
            return False

        return True

    def get_user_plan(self, user_id: int) -> str:
        user = self.get_user(int(user_id))
        if not user:
            user = self.register_user(int(user_id))
        return user.get("plan", PLAN_FREE)

    def is_plan_active(self, user_id: int) -> bool:
        user = self.get_user(int(user_id))
        if not user:
            return False
        return self.is_user_active(user)

    def upgrade_plan(self, user_id: int, plan: str):
        """
        Activa manualmente Plus o Premium.
        """
        user_id = int(user_id)
        if plan not in [PLAN_PLUS, PLAN_PREMIUM]:
            raise ValueError("Plan inválido")

        expires = datetime.utcnow() + timedelta(
            days=Config.PLAN_PLUS_DAYS if plan == PLAN_PLUS else Config.PLAN_PREMIUM_DAYS
        )

        self.collection.update_one(
            {"user_id": user_id},
            {"$set": {"plan": plan, "plan_expires_at": expires, "status": USER_ACTIVE}},
            upsert=True,
        )

        logger.info(f"Plan activado | Usuario: {user_id} | Plan: {plan}")

    def block_user(self, user_id: int):
        """
        Bloquea permanentemente un usuario.
        """
        user_id = int(user_id)
        self.collection.update_one(
            {"user_id": user_id},
            {"$set": {"status": USER_BLOCKED}},
            upsert=False,
        )
        logger.warning(f"Usuario bloqueado | ID: {user_id}")

    def increment_policy_violation(self, user_id: int):
        """
        Incrementa violaciones de política y bloquea si excede el límite.
        """
        user_id = int(user_id)
        user = self.get_user(user_id)
        if not user:
            return

        violations = int(user.get("policy_violations", 0)) + 1
        update = {"policy_violations": violations}

        if violations >= int(Config.MAX_POLICY_VIOLATIONS):
            update["status"] = USER_BLOCKED
            logger.warning(f"Usuario bloqueado por violaciones | ID: {user_id}")

        self.collection.update_one({"user_id": user_id}, {"$set": update})


# ─────────────────────────────────────────────────────────────
# WRAPPERS (para compatibilidad con handlers existentes)
# ─────────────────────────────────────────────────────────────

_user_service = UserService()


def register_user_if_not_exists(telegram_id: int, username: Optional[str] = None, chat_id: Optional[int] = None) -> dict:
    """
    Usado por telegram_bot/handlers/start.py (importa esta función).
    Guardamos chat_id para push.
    """
    return _user_service.register_user(
        user_id=int(telegram_id),
        username=username,
        telegram_chat_id=int(chat_id) if chat_id is not None else int(telegram_id),
    )


def get_user_plan(user_id: int) -> str:
    """
    Usado por telegram_bot/handlers/signals.py
    """
    return _user_service.get_user_plan(int(user_id))


def is_plan_active(user_id: int) -> bool:
    """
    Usado por telegram_bot/handlers/signals.py
    """
    return _user_service.is_plan_active(int(user_id))
