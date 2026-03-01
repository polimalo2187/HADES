# services/telegram_push_service.py

from __future__ import annotations

import requests
from typing import Optional

from core.config import Config
from core.logger import get_logger

logger = get_logger(__name__)


class TelegramPushService:
    """
    Envío de mensajes push por HTTP directo a Telegram Bot API.
    (No requiere loop async; funciona bien desde APScheduler).
    """

    def __init__(self):
        self.cfg = Config()
        if not self.cfg.TELEGRAM_BOT_TOKEN:
            raise RuntimeError("TELEGRAM_BOT_TOKEN no configurado")
        self.base_url = f"https://api.telegram.org/bot{self.cfg.TELEGRAM_BOT_TOKEN}"

    def send_message(self, chat_id: int, text: str, disable_web_page_preview: bool = True) -> bool:
        """
        Retorna True si Telegram aceptó el envío.
        Si el bot está bloqueado o chat inválido, retorna False.
        """
        url = f"{self.base_url}/sendMessage"
        payload = {
            "chat_id": int(chat_id),
            "text": text,
            "disable_web_page_preview": bool(disable_web_page_preview),
        }

        try:
            resp = requests.post(url, json=payload, timeout=10)
        except Exception as e:
            logger.exception(f"Error enviando push a chat_id={chat_id}: {e}")
            return False

        if resp.status_code != 200:
            # 403: bot blocked by user / 400: chat not found, etc.
            logger.warning(f"Push falló chat_id={chat_id} status={resp.status_code} body={resp.text[:200]}")
            return False

        data = resp.json()
        ok = bool(data.get("ok"))
        if not ok:
            logger.warning(f"Push no-ok chat_id={chat_id} body={str(data)[:300]}")
        return ok
