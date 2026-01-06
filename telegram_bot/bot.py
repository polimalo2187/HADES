# telegram_bot/bot.py

import logging
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
)
from core.config import settings
from core.logger import get_logger

# Handlers
from telegram_bot.handlers.start import start_handler
from telegram_bot.handlers.user_menu import user_menu_handler
from telegram_bot.handlers.signals import signals_handler
from telegram_bot.handlers.account import account_handler
from telegram_bot.handlers.plans import plans_handler
from telegram_bot.handlers.policies import policies_handler
from telegram_bot.handlers.support import support_handler
from telegram_bot.handlers.admin.panel import admin_panel_handler

logger = get_logger(__name__)


def create_application() -> Application:
    """
    Crea y configura la aplicación principal del bot de Telegram.
    No contiene lógica de negocio.
    """

    application = Application.builder().token(settings.TELEGRAM_BOT_TOKEN).build()

    # Comandos base
    application.add_handler(CommandHandler("start", start_handler))

    # Menú usuario (botones)
    application.add_handler(CallbackQueryHandler(user_menu_handler, pattern="^menu_"))
    application.add_handler(CallbackQueryHandler(signals_handler, pattern="^signal_"))
    application.add_handler(CallbackQueryHandler(account_handler, pattern="^account_"))
    application.add_handler(CallbackQueryHandler(plans_handler, pattern="^plans_"))
    application.add_handler(CallbackQueryHandler(policies_handler, pattern="^policy_"))
    application.add_handler(CallbackQueryHandler(support_handler, pattern="^support_"))

    # Panel administrador
    application.add_handler(
        CallbackQueryHandler(admin_panel_handler, pattern="^admin_")
    )

    logger.info("🤖 Bot de Telegram inicializado correctamente")
    return application


def run_bot():
    """
    Arranca el bot de Telegram.
    """
    app = create_application()
    logger.info("🚀 Bot HADES en ejecución")
    app.run_polling()


if __name__ == "__main__":
    run_bot()
