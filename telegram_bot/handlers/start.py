# telegram_bot/handlers/start.py

from telegram import Update
from telegram.ext import ContextTypes

from core.logger import get_logger
from telegram_bot.keyboards import main_menu_keyboard
from services.user_service import register_user_if_not_exists

logger = get_logger(__name__)


async def start_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Handler del comando /start.
    - Registra el usuario si no existe
    - Asigna plan Free (5 días) si es nuevo
    - Limpia el chat
    - Muestra el menú principal
    """

    user = update.effective_user
    chat_id = update.effective_chat.id

    # Registrar usuario (si no existe)
    register_user_if_not_exists(
        telegram_id=user.id,
        username=user.username,
    )

    # Limpiar mensajes anteriores (mejor UX)
    try:
        await context.bot.delete_message(
            chat_id=chat_id,
            message_id=update.message.message_id - 1
        )
    except Exception:
        pass

    logger.info(f"👤 Usuario iniciado: {user.id}")

    await update.message.reply_text(
        text=(
            "🔥 *Bienvenido a HADES*\n\n"
            "El bot de señales Forex de alta precisión.\n\n"
            "Selecciona una opción del menú:"
        ),
        reply_markup=main_menu_keyboard(),
        parse_mode="Markdown"
    )
