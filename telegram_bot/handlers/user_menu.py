# telegram_bot/handlers/user_menu.py

from telegram import Update
from telegram.ext import ContextTypes

from core.logger import get_logger
from telegram_bot.keyboards import main_menu_keyboard

logger = get_logger(__name__)


async def user_menu_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Handler del menú principal.
    Controla la navegación entre los botones del usuario.
    """

    query = update.callback_query
    await query.answer()

    action = query.data

    logger.info(f"📌 Acción menú usuario: {action}")

    # Volver al menú principal
    if action == "menu_back":
        await query.edit_message_text(
            text="Selecciona una opción del menú:",
            reply_markup=main_menu_keyboard()
        )
        return

    # Redirección controlada (los handlers específicos se encargan)
    # Aquí solo reenviamos el callback
    await context.application.process_update(update)
