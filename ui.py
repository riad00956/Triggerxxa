from telebot import types
from config import BASIC_INTERVALS, PRIME_INTERVALS

def main_menu(is_prime):
    kb = types.InlineKeyboardMarkup(row_width=2)
    kb.add(types.InlineKeyboardButton("➕ Add Monitor", callback_data="add_mon"),
           types.InlineKeyboardButton("📋 My Monitors", callback_data="list_mon"))
    if not is_prime:
        kb.add(types.InlineKeyboardButton("💎 Unlock PRIME", callback_data="redeem_key"))
    kb.add(types.InlineKeyboardButton("🛠 Admin", callback_data="admin_panel"))
    return kb

def intervals_kb(is_prime):
    kb = types.InlineKeyboardMarkup(row_width=2)
    source = PRIME_INTERVALS if is_prime else BASIC_INTERVALS
    for label, sec in source.items():
        kb.add(types.InlineKeyboardButton(label, callback_data=f"set_int_{sec}"))
    kb.add(types.InlineKeyboardButton("🔙 Back", callback_data="go_home"))
    return kb

def monitor_list_kb(monitors):
    kb = types.InlineKeyboardMarkup(row_width=1)
    for m in monitors:
        icon = "🟢" if m['last_status'] == "UP" else "🔴" if m['last_status'] == "DOWN" else "⏳"
        kb.add(types.InlineKeyboardButton(f"{icon} {m['url']}", callback_data=f"view_{m['id']}"))
    kb.add(types.InlineKeyboardButton("🏠 Home", callback_data="go_home"))
    return kb

def monitor_view_kb(m_id):
    kb = types.InlineKeyboardMarkup(row_width=2)
    kb.add(types.InlineKeyboardButton("🗑 Delete", callback_data=f"del_{m_id}"),
           types.InlineKeyboardButton("🔄 Refresh", callback_data=f"view_{m_id}"))
    kb.add(types.InlineKeyboardButton("🔙 Back", callback_data="list_mon"))
    return kb

def admin_kb():
    kb = types.InlineKeyboardMarkup(row_width=1)
    kb.add(types.InlineKeyboardButton("🔑 Generate Key", callback_data="adm_gen_key"),
           types.InlineKeyboardButton("📊 System Stats", callback_data="adm_stats"),
           types.InlineKeyboardButton("🏠 Home", callback_data="go_home"))
    return kb
