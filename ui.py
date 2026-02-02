from telebot import types
from config import PLANS, INTERVALS

def main_menu_kb(user_plan):
    kb = types.InlineKeyboardMarkup(row_width=2)
    kb.add(types.InlineKeyboardButton("➕ Add Monitor", callback_data="mon:add"))
    kb.add(types.InlineKeyboardButton("📋 My Monitors", callback_data="mon:list:0"))
    if user_plan == 'BASIC':
        kb.add(types.InlineKeyboardButton("💎 Upgrade to PRIME", callback_data="prime:redeem"))
    kb.add(types.InlineKeyboardButton("📊 Analytics", callback_data="stats"))
    return kb

def intervals_kb(url):
    kb = types.InlineKeyboardMarkup(row_width=2)
    for label in INTERVALS.keys():
        kb.add(types.InlineKeyboardButton(label, callback_data=f"mon:save:{label}"))
    kb.add(types.InlineKeyboardButton("❌ Cancel", callback_data="menu:home"))
    return kb

def monitors_list_kb(monitors, page=0):
    kb = types.InlineKeyboardMarkup(row_width=1)
    # Simple pagination: 5 per page
    start = page * 5
    end = start + 5
    for m in monitors[start:end]:
        status_icon = "🟢" if m['status'] == "UP" else "🔴" if m['status'] == "DOWN" else "⏳"
        kb.add(types.InlineKeyboardButton(f"{status_icon} {m['url'][:25]}", callback_data=f"mon:view:{m['id']}"))
    
    nav = []
    if start > 0: nav.append(types.InlineKeyboardButton("⬅️", callback_data=f"mon:list:{page-1}"))
    if end < len(monitors): nav.append(types.InlineKeyboardButton("➡️", callback_data=f"mon:list:{page+1}"))
    if nav: kb.row(*nav)
    
    kb.add(types.InlineKeyboardButton("🏠 Back", callback_data="menu:home"))
    return kb

def monitor_view_kb(m_id):
    kb = types.InlineKeyboardMarkup(row_width=2)
    kb.add(types.InlineKeyboardButton("🔄 Refresh", callback_data=f"mon:view:{m_id}"))
    kb.add(types.InlineKeyboardButton("🗑 Delete", callback_data=f"mon:del:{m_id}"))
    kb.add(types.InlineKeyboardButton("🔙 Back", callback_data="mon:list:0"))
    return kb

def admin_kb():
    kb = types.InlineKeyboardMarkup(row_width=1)
    kb.add(types.InlineKeyboardButton("🔑 Generate Key", callback_data="adm:genkey"))
    kb.add(types.InlineKeyboardButton("👥 User Stats", callback_data="adm:users"))
    kb.add(types.InlineKeyboardButton("🏠 Close", callback_data="menu:home"))
    return kb
