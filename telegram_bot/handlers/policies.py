# telegram_bot/handlers/policies.py

from telegram import Update
from telegram.ext import ContextTypes

from core.logger import get_logger
from telegram_bot.keyboards import back_to_main_menu

logger = get_logger(__name__)


async def policies_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Handler del botón 'Políticas de Seguridad'.

    Muestra las normas, restricciones y consecuencias del uso del bot HADES.
    """

    query = update.callback_query
    await query.answer()

    logger.info(f"🛡️ Usuario consulta políticas: {query.from_user.id}")

    text = (
        "🛡️ *Políticas de Seguridad – HADES*\n\n"
        "HADES es un sistema privado de señales de trading.\n\n"
        "📌 *Está estrictamente prohibido:*\n"
        "• Copiar, reenviar o compartir señales\n"
        "• Tomar capturas de pantalla para redistribución\n"
        "• Vender o regalar el acceso\n"
        "• Usar el contenido con fines comerciales externos\n\n"
        "⚠️ *Medidas de Seguridad:*\n"
        "• Cada señal es personalizada con un ID único\n"
        "• El sistema monitorea comportamientos sospechosos\n"
        "• Cualquier violación resultará en bloqueo permanente\n\n"
        "📜 *Responsabilidad:*\n"
        "El trading conlleva riesgo. HADES proporciona análisis\n"
        "técnico, no garantiza resultados ni beneficios.\n\n"
        "Al utilizar este bot aceptas automáticamente\n"
        "todas las políticas aquí descritas."
    )

    await query.edit_message_text(
        text=text,
        reply_markup=back_to_main_menu(),
        parse_mode="Markdown"
    )
