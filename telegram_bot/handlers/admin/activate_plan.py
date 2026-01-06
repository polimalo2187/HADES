# telegram_bot/handlers/admin/activate_plan.py

from telegram import Update
from telegram.ext import ContextTypes, MessageHandler, filters

from core.logger import get_logger
from telegram_bot.keyboards import admin_plan_selection_keyboard, back_to_main_menu
from services.admin_service import is_admin
from services.user_service import activate_user_plan

logger = get_logger(__name__)


# Estado temporal en memoria (solo para el flujo admin)
ADMIN_STATE = {}


async def activate_plan_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Inicia el flujo de activación de plan.
    Solicita el ID del usuario.
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

    ADMIN_STATE[admin_id] = {"step": "awaiting_user_id"}

    await query.edit_message_text(
        text="🆔 *Activación de Plan*\n\nEnvía el ID del usuario:",
        reply_markup=back_to_main_menu(),
        parse_mode="Markdown"
    )


async def receive_user_id(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Recibe el ID del usuario a activar.
    """

    admin_id = update.effective_user.id

    if admin_id not in ADMIN_STATE:
        return

    if ADMIN_STATE[admin_id].get("step") != "awaiting_user_id":
        return

    try:
        user_id = int(update.message.text.strip())
    except ValueError:
        await update.message.reply_text("❌ ID inválido. Intenta nuevamente.")
        return

    ADMIN_STATE[admin_id] = {
        "step": "awaiting_plan",
        "user_id": user_id
    }

    await update.message.reply_text(
        text=f"Selecciona el plan a activar para el usuario `{user_id}`:",
        reply_markup=admin_plan_selection_keyboard(),
        parse_mode="Markdown"
    )


async def confirm_plan_activation(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Confirma y activa el plan seleccionado.
    """

    query = update.callback_query
    await query.answer()

    admin_id = query.from_user.id

    if admin_id not in ADMIN_STATE:
        return

    if ADMIN_STATE[admin_id].get("step") != "awaiting_plan":
        return

    user_id = ADMIN_STATE[admin_id]["user_id"]

    if query.data == "admin_plan_plus":
        plan = "plus"
    elif query.data == "admin_plan_premium":
        plan = "premium"
    else:
        await query.edit_message_text(
            text="❌ Operación cancelada.",
            reply_markup=back_to_main_menu()
        )
        ADMIN_STATE.pop(admin_id, None)
        return

    activate_user_plan(user_id, plan)

    await query.edit_message_text(
        text=f"✅ *Plan {plan.upper()} activado correctamente*\n\nUsuario ID: `{user_id}`",
        reply_markup=back_to_main_menu(),
        parse_mode="Markdown"
    )

    logger.info(f"✅ Admin {admin_id} activó plan {plan} para usuario {user_id}")

    ADMIN_STATE.pop(admin_id, None)
