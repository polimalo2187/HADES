# telegram_bot/handlers/plans.py

from telegram import Update
from telegram.ext import ContextTypes

from core.logger import get_logger
from telegram_bot.keyboards import plans_keyboard, back_to_main_menu
from core.config import settings

logger = get_logger(__name__)


async def plans_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Handler del botón 'Planes'.

    - Muestra planes disponibles (Plus / Premium)
    - Proporciona contactos de administradores para compra
    """

    query = update.callback_query
    await query.answer()

    action = query.data

    logger.info(f"💎 Usuario consulta planes: {query.from_user.id}")

    # Menú principal de planes
    if action == "plans_view":
        await query.edit_message_text(
            text=(
                "💎 *Planes Disponibles*\n\n"
                "⭐ *Plan Plus* — Acceso a señales de alta calidad\n"
                "🔥 *Plan Premium* — Acceso a las señales más fuertes del mercado\n\n"
                "Para adquirir un plan, selecciona una opción:"
            ),
            reply_markup=plans_keyboard(),
            parse_mode="Markdown"
        )
        return

    # Información Plan Plus
    if action == "plans_plus":
        await query.edit_message_text(
            text=(
                "⭐ *Plan Plus*\n\n"
                "✔ Señales Plus\n"
                "✔ Mayor frecuencia que Free\n"
                "✔ Alta precisión\n"
                "✔ Vigencia: 30 días\n\n"
                "📲 *Contacta a un administrador para activarlo:*\n"
                f"- {settings.ADMIN_CONTACT_1}\n"
                f"- {settings.ADMIN_CONTACT_2}"
            ),
            reply_markup=back_to_main_menu(),
            parse_mode="Markdown"
        )
        return

    # Información Plan Premium
    if action == "plans_premium":
        await query.edit_message_text(
            text=(
                "🔥 *Plan Premium*\n\n"
                "✔ Señales más fuertes del mercado\n"
                "✔ Máxima precisión\n"
                "✔ Prioridad absoluta\n"
                "✔ Vigencia: 30 días\n\n"
                "📲 *Contacta a un administrador para activarlo:*\n"
                f"- {settings.ADMIN_CONTACT_1}\n"
                f"- {settings.ADMIN_CONTACT_2}"
            ),
            reply_markup=back_to_main_menu(),
            parse_mode="Markdown"
        )
        return

    # Fallback
    await query.edit_message_text(
        text="Selecciona una opción válida.",
        reply_markup=back_to_main_menu()
    )
