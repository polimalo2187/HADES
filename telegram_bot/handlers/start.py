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
    - Guarda telegram_chat_id (para push)
    - Muestra el menú principal
    """
    user = update.effective_user
    chat = update.effective_chat
    if not user or not chat:
        return

    chat_id = int(chat.id)

    register_user_if_not_exists(
        telegram_id=int(user.id),
        username=user.username,
        chat_id=chat_id,
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
