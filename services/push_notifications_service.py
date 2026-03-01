# services/push_notifications_service.py

from __future__ import annotations

from datetime import datetime

from core.database import MongoDB
from core.logger import get_logger
from core.constants import PLAN_FREE, PLAN_PLUS, PLAN_PREMIUM, USER_ACTIVE, SIGNAL_ACTIVE
from signal_manager.signal_repository import SignalRepository
from services.telegram_push_service import TelegramPushService

logger = get_logger(__name__)


class PushNotificationsService:
    USERS_COLLECTION = "users"

    def __init__(self):
        self.db = MongoDB.get_db()
        self.users = self.db[self.USERS_COLLECTION]
        self.signals = SignalRepository()
        self.telegram = TelegramPushService()

    def run(self) -> dict:
        stats = {
            "checked_at": datetime.utcnow().isoformat(),
            "sent": 0,
            "failed": 0,
            "skipped_no_chat_id": 0,
            "skipped_inactive": 0,
            "skipped_duplicate": 0,
            "plans": {PLAN_FREE: 0, PLAN_PLUS: 0, PLAN_PREMIUM: 0},
        }

        for plan in (PLAN_FREE, PLAN_PLUS, PLAN_PREMIUM):
            signal = self.signals.get_active_signal_by_plan(plan)
            if not signal or signal.get("status") != SIGNAL_ACTIVE:
                continue

            signal_id = str(signal.get("id", "") or "").strip()
            if not signal_id:
                continue

            cursor = self.users.find(
                {
                    "plan": plan,                 # plan EXACTO (como pediste)
                    "status": USER_ACTIVE,
                    "push_enabled": {"$ne": False},
                },
                {
                    "_id": 0,
                    "user_id": 1,
                    "telegram_chat_id": 1,
                    "plan_expires_at": 1,
                    "last_notified_signal_id": 1,
                },
            )

            for u in cursor:
                expires = u.get("plan_expires_at")
                if expires and expires < datetime.utcnow():
                    stats["skipped_inactive"] += 1
                    continue

                chat_id = u.get("telegram_chat_id")
                if not chat_id:
                    stats["skipped_no_chat_id"] += 1
                    continue

                last_sent = str(u.get("last_notified_signal_id") or "").strip()
                if last_sent == signal_id:
                    stats["skipped_duplicate"] += 1
                    continue

                ok = self.telegram.send_message(
                    chat_id=int(chat_id),
                    text="🔔 Nueva señal disponible.",
                )

                if ok:
                    self.users.update_one(
                        {"user_id": int(u["user_id"])},
                        {"$set": {"last_notified_signal_id": signal_id, "last_push_at": datetime.utcnow()}},
                    )
                    stats["sent"] += 1
                    stats["plans"][plan] += 1
                else:
                    # Si falla, normalmente bot bloqueado / chat inválido: apagamos push para no reintentar infinito
                    self.users.update_one(
                        {"user_id": int(u["user_id"])},
                        {"$set": {"push_enabled": False, "last_push_failed_at": datetime.utcnow()}},
                    )
                    stats["failed"] += 1

        return stats
