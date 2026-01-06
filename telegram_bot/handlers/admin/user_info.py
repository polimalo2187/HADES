# telegram_bot/handlers/admin/user_info.py

from telegram import Update
from telegram.ext import ContextTypes

from core.logger import get_logger
from telegram_bot.keyboards import back_to_main_menu
from services.admin_service import is_admin
from services.user_service import get_users_statistics

logger = get_logger(__name__)


async def user_info_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Muestra información general de usuarios al administrador.

    - Total de usuarios
    - Usuarios Free / Plus / Premium
    """

    query = update.callback_query
    await query.answer()

    admin_id = query.from_user.id

    if not is_admin(admin_id):
        await query.edit_message_text(
            text="⛔ Acceso denegado.",
            reply_markup=back_to_main_menu()
        )
        return

    stats = get_users_statistics()

    text = (
        "📊 *Información de Usuarios – HADES*\n\n"
        f"👥 *Usuarios Totales:* {stats['total']}\n\n"
        f"🆓 *Free:* {stats['free']}\n"
        f"⭐ *Plus:* {stats['plus']}\n"
        f"🔥 *Premium:* {stats['premium']}\n"
    )

    await query.edit_message_text(
        text=text,
        reply_markup=back_to_main_menu(),
        parse_mode="Markdown"
    )

    logger.info(f"📊 Admin {admin_id} consultó estadísticas de usuarios")
