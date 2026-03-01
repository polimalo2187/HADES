# telegram_bot/handlers/start.py

from __future__ import annotations

from telegram import Update
from telegram.ext import ContextTypes

from core.logger import get_logger
from services.user_service import UserService

logger = get_logger(__name__)


async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    /start
    Registra usuario y guarda telegram_chat_id para push.
    """
    if not update.effective_user or not update.effective_chat:
        return

    user_id = int(update.effective_user.id)
    username = update.effective_user.username or ""
    chat_id = int(update.effective_chat.id)

    user_service = UserService()
    user_service.register_user(user_id=user_id, username=username, telegram_chat_id=chat_id)

    await update.message.reply_text(
        "👋 Bienvenido a HADES.\n"
        "Cuando haya una señal disponible según tu plan, recibirás un aviso.\n"
        "Usa el botón de señales para ver la señal."
    )
