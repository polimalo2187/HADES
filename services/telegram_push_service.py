# services/telegram_push_service.py

from __future__ import annotations

import requests

from core.config import Config
from core.logger import get_logger

logger = get_logger(__name__)


class TelegramPushService:
    def __init__(self):
        self.cfg = Config()
        token = getattr(self.cfg, "TELEGRAM_BOT_TOKEN", "") or ""
        if not token:
            raise RuntimeError("TELEGRAM_BOT_TOKEN no configurado en core/config.py o .env")
        self.base_url = f"https://api.telegram.org/bot{token}"

    def send_message(self, chat_id: int, text: str) -> bool:
        url = f"{self.base_url}/sendMessage"
        payload = {"chat_id": int(chat_id), "text": text, "disable_web_page_preview": True}

        try:
            resp = requests.post(url, json=payload, timeout=10)
        except Exception as e:
            logger.exception(f"Error push chat_id={chat_id}: {e}")
            return False

        if resp.status_code != 200:
            logger.warning(f"Push falló chat_id={chat_id} status={resp.status_code} body={resp.text[:200]}")
            return False

        data = resp.json()
        return bool(data.get("ok", False))
