# telegram_bot/handlers/account.py

from telegram import Update
from telegram.ext import ContextTypes

from core.logger import get_logger
from telegram_bot.keyboards import back_to_main_menu
from services.user_service import get_user_account_info

logger = get_logger(__name__)


async def account_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Handler del botón 'Mi Cuenta'.

    Muestra:
    - ID de usuario
    - Plan activo
    - Fecha de expiración
    """

    query = update.callback_query
    await query.answer()

    user_id = query.from_user.id

    logger.info(f"👤 Usuario consulta cuenta: {user_id}")

    account = get_user_account_info(user_id)

    if not account:
        await query.edit_message_text(
            text="⚠️ Error al obtener información de la cuenta.",
            reply_markup=back_to_main_menu()
        )
        return

    plan = account["plan"].upper()
    expires = account["expires_at"]

    text = (
        f"👤 *Mi Cuenta*\n\n"
        f"🆔 *ID:* `{user_id}`\n"
        f"💼 *Plan:* {plan}\n"
        f"⏳ *Vigencia:* {expires}\n\n"
    )

    if plan == "FREE":
        text += (
            "ℹ️ Este es un plan de prueba con duración limitada.\n"
            "Para acceso completo, adquiere un plan Plus o Premium."
        )

    await query.edit_message_text(
        text=text,
        reply_markup=back_to_main_menu(),
        parse_mode="Markdown"
    )
