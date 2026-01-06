# telegram_bot/keyboards.py

from telegram import InlineKeyboardButton, InlineKeyboardMarkup


# =========================
# MENÚ PRINCIPAL USUARIO
# =========================
def main_menu_keyboard():
    keyboard = [
        [InlineKeyboardButton("📊 Ver Señal", callback_data="signal_view")],
        [InlineKeyboardButton("👤 Mi Cuenta", callback_data="account_info")],
        [InlineKeyboardButton("💎 Planes", callback_data="plans_view")],
        [InlineKeyboardButton("🔍 Análisis de Señal", callback_data="signal_analysis")],
        [InlineKeyboardButton("🛡️ Políticas de Seguridad", callback_data="policy_view")],
        [InlineKeyboardButton("🆘 Soporte", callback_data="support_view")],
    ]
    return InlineKeyboardMarkup(keyboard)


# =========================
# BOTÓN VOLVER
# =========================
def back_to_main_menu():
    keyboard = [
        [InlineKeyboardButton("⬅️ Volver al Menú Principal", callback_data="menu_back")]
    ]
    return InlineKeyboardMarkup(keyboard)


# =========================
# MENÚ PLANES
# =========================
def plans_keyboard():
    keyboard = [
        [InlineKeyboardButton("⭐ Plan Plus", callback_data="plans_plus")],
        [InlineKeyboardButton("🔥 Plan Premium", callback_data="plans_premium")],
        [InlineKeyboardButton("⬅️ Volver", callback_data="menu_back")],
    ]
    return InlineKeyboardMarkup(keyboard)


# =========================
# PANEL ADMINISTRADOR
# =========================
def admin_panel_keyboard():
    keyboard = [
        [InlineKeyboardButton("✅ Activar Plan", callback_data="admin_activate_plan")],
        [InlineKeyboardButton("📊 Información de Usuarios", callback_data="admin_user_info")],
        [InlineKeyboardButton("🚫 Bloquear Usuario", callback_data="admin_block_user")],
        [InlineKeyboardButton("⬅️ Volver al Menú Principal", callback_data="menu_back")],
    ]
    return InlineKeyboardMarkup(keyboard)


# =========================
# SELECCIÓN DE PLAN (ADMIN)
# =========================
def admin_plan_selection_keyboard():
    keyboard = [
        [InlineKeyboardButton("⭐ Activar Plus", callback_data="admin_plan_plus")],
        [InlineKeyboardButton("🔥 Activar Premium", callback_data="admin_plan_premium")],
        [InlineKeyboardButton("⬅️ Cancelar", callback_data="menu_back")],
    ]
    return InlineKeyboardMarkup(keyboard)
