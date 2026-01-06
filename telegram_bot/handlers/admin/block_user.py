# telegram_bot/handlers/admin/block_user.py

from telegram import Update
from telegram.ext import ContextTypes, ConversationHandler

from core.logger import get_logger
from telegram_bot.keyboards import back_to_main_menu
from services.admin_service import is_admin
from services.user_service import block_user_by_id

logger = get_logger(__name__)

ASK_USER_ID = 1


async def block_user_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Inicia el flujo para bloquear un usuario por ID
    """
    query = update.callback_query
    await query.answer()

    admin_id = query.from_user.id

    if not is_admin(admin_id):
        await query.edit_message_text(
            text="⛔ Acceso denegado.",
            reply_markup=back_to_main_menu()
        )
        return ConversationHandler.END

    await query.edit_message_text(
        text=(
            "🚫 *Bloqueo de Usuario – HADES*\n\n"
            "Envía el *ID del usuario* que deseas bloquear.\n\n"
            "⚠️ Esta acción es *permanente*."
        ),
        parse_mode="Markdown"
    )

    return ASK_USER_ID


async def block_user_confirm(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Bloquea definitivamente al usuario
    """
    admin_id = update.effective_user.id
    user_id_text = update.message.text.strip()

    if not user_id_text.isdigit():
        await update.message.reply_text(
            "❌ El ID debe ser numérico.\n\nIntenta nuevamente:"
        )
        return ASK_USER_ID

    user_id = int(user_id_text)

    success = block_user_by_id(user_id)

    if success:
        text = (
            "✅ *Usuario bloqueado exitosamente*\n\n"
            f"🆔 ID: `{user_id}`\n\n"
            "⛔ No podrá volver a registrarse en el sistema."
        )
        logger.warning(f"🚫 Admin {admin_id} bloqueó al usuario {user_id}")
    else:
        text = (
            "❌ *No se pudo bloquear al usuario*\n\n"
            "El usuario no existe o ya estaba bloqueado."
        )

    await update.message.reply_text(
        text=text,
        reply_markup=back_to_main_menu(),
        parse_mode="Markdown"
    )

    return ConversationHandler.END
