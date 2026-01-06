# telegram_bot/handlers/admin/panel.py

from telegram import Update
from telegram.ext import ContextTypes

from core.logger import get_logger
from core.config import settings
from telegram_bot.keyboards import admin_panel_keyboard, back_to_main_menu
from services.admin_service import is_admin

logger = get_logger(__name__)


async def admin_panel_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Panel de control del administrador.

    - Verifica permisos de administrador
    - Muestra opciones administrativas
    """

    query = update.callback_query
    await query.answer()

    user_id = query.from_user.id

    logger.info(f"🛠️ Acceso a panel admin solicitado por: {user_id}")

    # Validar permisos
    if not is_admin(user_id):
        await query.edit_message_text(
            text="⛔ Acceso denegado.\nNo tienes permisos de administrador.",
            reply_markup=back_to_main_menu()
        )
        logger.warning(f"❌ Acceso admin denegado: {user_id}")
        return

    await query.edit_message_text(
        text=(
            "🛠️ *Panel de Control – Administrador*\n\n"
            "Desde aquí tienes control total del sistema HADES.\n"
            "Selecciona una acción:"
        ),
        reply_markup=admin_panel_keyboard(),
        parse_mode="Markdown"
    )
