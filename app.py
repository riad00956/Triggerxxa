import uuid
from flask import Flask
from threading import Thread
import telebot
from config import BOT_TOKEN, ADMIN_IDS, PORT
from database import db
from ui import main_menu, intervals_kb, monitor_list_kb, monitor_view_kb, admin_kb
from utils import is_valid_url
import core

bot = telebot.TeleBot(BOT_TOKEN)
server = Flask(__name__)
user_data = {} # Temporary state storage

@server.route('/')
def index(): return "Bot is Running", 200

def run_flask():
    server.run(host="0.0.0.0", port=PORT)

@bot.message_handler(commands=['start'])
def start(message):
    user = db.get_user(message.from_user.id, message.from_user.username)
    bot.send_message(message.chat.id, f"👋 Hello {message.from_user.first_name}!\nSelect an option:", 
                     reply_markup=main_menu(user['is_prime']))

@bot.callback_query_handler(func=lambda call: True)
def handle_query(call):
    uid = call.from_user.id
    user = db.get_user(uid)
    
    if call.data == "go_home":
        bot.edit_message_text("🏠 Main Menu", uid, call.message.id, reply_markup=main_menu(user['is_prime']))
    
    elif call.data == "add_mon":
        msg = bot.send_message(uid, "🔗 Send the URL to monitor (including http/https):")
        bot.register_next_step_handler(msg, process_url)
        
    elif call.data.startswith("set_int_"):
        interval = int(call.data.split("_")[-1])
        url = user_data.get(uid)
        m_id = db.add_monitor(uid, url, interval)
        core.setup_monitor(m_id, interval)
        bot.edit_message_text(f"✅ Monitoring started for {url}", uid, call.message.id, reply_markup=main_menu(user['is_prime']))

    elif call.data == "list_mon":
        mons = db.conn.execute("SELECT * FROM monitors WHERE user_id=?", (uid,)).fetchall()
        bot.edit_message_text("📋 Your Monitors:", uid, call.message.id, reply_markup=monitor_list_kb(mons))

    elif call.data.startswith("view_"):
        m_id = call.data.split("_")[1]
        m = db.conn.execute("SELECT * FROM monitors WHERE id=?", (m_id,)).fetchone()
        logs = db.conn.execute("SELECT * FROM logs WHERE monitor_id=? ORDER BY timestamp DESC LIMIT 5", (m_id,)).fetchall()
        log_str = "\n".join([f"{l['timestamp'][11:19]} - {l['status']} ({l['response_time']}s)" for l in logs])
        bot.edit_message_text(f"🌐 URL: {m['url']}\n⏱ Interval: {m['interval']}s\n📊 Status: {m['last_status']}\n\nRecent Logs:\n{log_str}", 
                              uid, call.message.id, reply_markup=monitor_view_kb(m_id))

    elif call.data.startswith("del_"):
        m_id = call.data.split("_")[1]
        db.delete_monitor(m_id)
        try: core.scheduler.remove_job(f"job_{m_id}") 
        except: pass
        bot.answer_callback_query(call.id, "Monitor Deleted")
        handle_query(types.CallbackQuery(id=call.id, from_user=call.from_user, chat_instance=call.chat_instance, message=call.message, data="list_mon"))

    elif call.data == "redeem_key":
        msg = bot.send_message(uid, "🔑 Please enter your PRIME Key:")
        bot.register_next_step_handler(msg, process_key)

    elif call.data == "admin_panel":
        if uid not in ADMIN_IDS: return bot.answer_callback_query(call.id, "Access Denied")
        bot.edit_message_text("🛠 Admin Panel", uid, call.message.id, reply_markup=admin_kb())

    elif call.data == "adm_gen_key":
        new_key = str(uuid.uuid4())[:13].upper()
        db.conn.execute("INSERT INTO keys (key, created_at) VALUES (?, ?)", (new_key, datetime.now()))
        db.conn.commit()
        bot.send_message(uid, f"🔑 New Key Generated:\n`{new_key}`", parse_mode="Markdown")

def process_url(message):
    if is_valid_url(message.text):
        user_data[message.from_user.id] = message.text
        user = db.get_user(message.from_user.id)
        bot.send_message(message.chat.id, "Select Interval:", reply_markup=intervals_kb(user['is_prime']))
    else:
        bot.send_message(message.chat.id, "❌ Invalid URL. Use /start to try again.")

def process_key(message):
    key_text = message.text.strip()
    key = db.conn.execute("SELECT * FROM keys WHERE key=? AND is_redeemed=0", (key_text,)).fetchone()
    if key:
        db.conn.execute("UPDATE keys SET is_redeemed=1, user_id=? WHERE key=?", (message.from_user.id, key_text))
        db.update_user_prime(message.from_user.id)
        bot.send_message(message.chat.id, "💎 PRIME Unlocked Successfully! Restarting menu...")
        start(message)
    else:
        bot.send_message(message.chat.id, "❌ Invalid or already used key.")

if __name__ == "__main__":
    core.restore_jobs()
    Thread(target=run_flask).start()
    print(f"Server started on port {PORT}")
    bot.infinity_polling()
