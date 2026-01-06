# telegram_bot/handlers/support.py

from telegram import Update
from telegram.ext import ContextTypes

from core.logger import get_logger
from telegram_bot.keyboards import back_to_main_menu
from core.config import settings

logger = get_logger(__name__)


async def support_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Handler del botón 'Soporte'.

    Proporciona enlaces directos al soporte técnico del bot.
    """

    query = update.callback_query
    await query.answer()

    logger.info(f"🆘 Usuario solicita soporte: {query.from_user.id}")

    text = (
        "🆘 *Soporte Técnico – HADES*\n\n"
        "Si necesitas ayuda, soporte técnico o información adicional,\n"
        "puedes contactar directamente con nuestro equipo:\n\n"
        f"📲 *Administrador 1:* {settings.ADMIN_CONTACT_1}\n"
        f"📲 *Administrador 2:* {settings.ADMIN_CONTACT_2}\n\n"
        "⏱ Horario de atención: 24/7\n"
        "Responderemos lo antes posible."
    )

    await query.edit_message_text(
        text=text,
        reply_markup=back_to_main_menu(),
        parse_mode="Markdown"
    )
