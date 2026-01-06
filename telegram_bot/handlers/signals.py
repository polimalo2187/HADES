# telegram_bot/handlers/signals.py

from telegram import Update
from telegram.ext import ContextTypes

from core.logger import get_logger
from telegram_bot.keyboards import back_to_main_menu
from services.user_service import get_user_plan, is_plan_active
from services.signal_service import get_active_signal_for_user

logger = get_logger(__name__)


async def signals_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Handler del botón 'Ver Señal'.

    - Verifica plan activo
    - Muestra solo la señal correspondiente al plan
    - Señales personalizadas con ID único
    - Si no hay señal, informa al usuario
    """

    query = update.callback_query
    await query.answer()

    user_id = query.from_user.id

    logger.info(f"📊 Usuario solicita señal: {user_id}")

    # Verificar plan activo
    if not is_plan_active(user_id):
        await query.edit_message_text(
            text=(
                "⛔ *Plan expirado*\n\n"
                "Tu plan actual ha vencido.\n"
                "Obtén un plan Plus o Premium para seguir recibiendo señales."
            ),
            reply_markup=back_to_main_menu(),
            parse_mode="Markdown"
        )
        return

    # Obtener plan del usuario
    plan = get_user_plan(user_id)

    # Obtener señal activa según plan
    signal = get_active_signal_for_user(user_id, plan)

    if not signal:
        await query.edit_message_text(
            text=(
                "📭 *No hay señales disponibles*\n\n"
                "Actualmente no existen señales que cumplan\n"
                "los criterios estrictos de calidad de HADES.\n\n"
                "Seguimos analizando el mercado 24/7."
            ),
            reply_markup=back_to_main_menu(),
            parse_mode="Markdown"
        )
        return

    # Mostrar señal (personalizada)
    signal_text = (
        f"🔥 *SEÑAL {signal['plan'].upper()}*\n\n"
        f"📈 *Par:* {signal['pair']}\n"
        f"⏱ *Timeframe:* {signal['timeframe']}\n"
        f"🎯 *Dirección:* {signal['direction']}\n\n"
        f"*Entrada:* {signal['entry']}\n\n"
        f"🟢 *Conservador*\n"
        f"TP: {signal['tp_conservative']} | SL: {signal['sl_conservative']}\n\n"
        f"🟡 *Moderado*\n"
        f"TP: {signal['tp_moderate']} | SL: {signal['sl_moderate']}\n\n"
        f"🔴 *Agresivo*\n"
        f"TP: {signal['tp_aggressive']} | SL: {signal['sl_aggressive']}\n\n"
        f"⏳ *Tiempo estimado:* {signal['estimated_time']}\n\n"
        f"🆔 *ID de señal:* `{signal['signal_id']}`\n\n"
        f"⚠️ *Prohibido copiar o compartir esta señal.*\n"
        f"Cualquier violación resultará en bloqueo permanente."
    )

    await query.edit_message_text(
        text=signal_text,
        reply_markup=back_to_main_menu(),
        parse_mode="Markdown"
    )
