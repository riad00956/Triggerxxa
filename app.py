import telebot
import uuid
from config import BOT_TOKEN, ADMIN_IDS, PLANS
from database import Database
from core import MonitorEngine
from ui import main_menu_kb, intervals_kb, monitors_list_kb, monitor_view_kb, admin_kb
from utils import is_valid_url, format_time

bot = telebot.TeleBot(BOT_TOKEN)
db = Database("uptime.db")
engine = MonitorEngine(db, bot)

# Temp storage for state
user_state = {}

@bot.message_handler(commands=['start'])
def start_cmd(message):
    user = db.get_user(message.from_user.id)
    text = f"👋 *Welcome to Uptime Monitor*\n\nYour Plan: {PLANS[user['plan']]['label']}"
    bot.send_message(message.chat.id, text, parse_mode="Markdown", reply_markup=main_menu_kb(user['plan']))

@bot.message_handler(commands=['admin'])
def admin_cmd(message):
    if message.from_user.id not in ADMIN_IDS: return
    bot.send_message(message.chat.id, "🛠 *Admin Panel*", parse_mode="Markdown", reply_markup=admin_kb())

@bot.callback_query_handler(func=lambda call: True)
def handle_callbacks(call):
    uid = call.from_user.id
    data = call.data
    user = db.get_user(uid)

    if data == "menu:home":
        bot.edit_message_text(f"👋 *Welcome*\nPlan: {PLANS[user['plan']]['label']}", 
                              uid, call.message.message_id, parse_mode="Markdown", 
                              reply_markup=main_menu_kb(user['plan']))

    elif data == "mon:add":
        msg = bot.send_message(uid, "🔗 Please send the URL (include http/https):")
        bot.register_next_step_handler(msg, process_url_input)

    elif data.startswith("mon:save:"):
        interval = data.split(":")[-1]
        url = user_state.get(uid)
        if url:
            m_id = db.add_monitor(uid, url, interval)
            engine.schedule_monitor(m_id, interval)
            bot.edit_message_text("✅ Monitor added and started!", uid, call.message.message_id, reply_markup=main_menu_kb(user['plan']))
            del user_state[uid]

    elif data.startswith("mon:list:"):
        page = int(data.split(":")[-1])
        monitors = db.get_monitors(uid)
        bot.edit_message_text(f"📋 *Your Monitors* ({len(monitors)})", uid, call.message.message_id, 
                              parse_mode="Markdown", reply_markup=monitors_list_kb(monitors, page))

    elif data.startswith("mon:view:"):
        m_id = int(data.split(":")[-1])
        m = db.conn.execute("SELECT * FROM monitors WHERE id = ?", (m_id,)).fetchone()
        logs = db.get_logs(m_id)
        log_text = "\n".join([f"`{format_time(l['timestamp'])}` - {l['status_code']} ({l['response_time']}s)" for l in logs[:10]])
        text = f"🌐 *URL:* {m['url']}\n⏱ *Interval:* {m['interval']}\n📊 *Status:* {m['status']}\n\n*Last Logs:*\n{log_text if log_text else 'No logs yet'}"
        bot.edit_message_text(text, uid, call.message.message_id, parse_mode="Markdown", reply_markup=monitor_view_kb(m_id))

    elif data.startswith("mon:del:"):
        m_id = int(data.split(":")[-1])
        db.delete_monitor(m_id)
        engine.stop_job(m_id)
        bot.answer_callback_query(call.id, "Deleted!")
        handle_callbacks(types.CallbackQuery(id=call.id, from_user=call.from_user, chat_instance=call.chat_instance, message=call.message, data="mon:list:0"))

    elif data == "prime:redeem":
        msg = bot.send_message(uid, "🔑 Enter your PRIME Key:")
        bot.register_next_step_handler(msg, process_key_redeem)

    elif data == "adm:genkey":
        new_key = str(uuid.uuid4())[:8].upper()
        db.create_key(new_key)
        bot.send_message(uid, f"🆕 *New Key Created:*\n`{new_key}`", parse_mode="Markdown")

def process_url_input(message):
    url = message.text
    if is_valid_url(url):
        user_state[message.from_user.id] = url
        bot.send_message(message.chat.id, "Select check interval:", reply_markup=intervals_kb(url))
    else:
        bot.send_message(message.chat.id, "❌ Invalid URL. Try again from menu.")

def process_key_redeem(message):
    key = message.text.strip()
    if db.use_key(key, message.from_user.id):
        db.update_user_plan(message.from_user.id, 'PRIME')
        bot.send_message(message.chat.id, "🎉 *Congratulations!* PRIME unlocked.", parse_mode="Markdown")
    else:
        bot.send_message(message.chat.id, "❌ Invalid or already used key.")

if __name__ == "__main__":
    print("Bot is starting...")
    engine.restore_all_jobs()
    bot.infinity_polling()
