import sqlite3
from datetime import datetime

class Database:
    def __init__(self, db_path="uptime.db"):
        self.conn = sqlite3.connect(db_path, check_same_thread=False)
        self.conn.row_factory = sqlite3.Row
        self.init_db()

    def init_db(self):
        cursor = self.conn.cursor()
        cursor.execute('''CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY, username TEXT, is_prime INTEGER DEFAULT 0)''')
        cursor.execute('''CREATE TABLE IF NOT EXISTS monitors (
            id INTEGER PRIMARY KEY AUTOINCREMENT, user_id INTEGER, 
            url TEXT, interval INTEGER, last_status TEXT DEFAULT 'Pending')''')
        cursor.execute('''CREATE TABLE IF NOT EXISTS logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT, monitor_id INTEGER, 
            status TEXT, response_time REAL, timestamp DATETIME)''')
        cursor.execute('''CREATE TABLE IF NOT EXISTS keys (
            key TEXT PRIMARY KEY, is_redeemed INTEGER DEFAULT 0, 
            user_id INTEGER, created_at DATETIME)''')
        self.conn.commit()

    def get_user(self, user_id, username=None):
        user = self.conn.execute("SELECT * FROM users WHERE id=?", (user_id,)).fetchone()
        if not user and username:
            self.conn.execute("INSERT INTO users (id, username) VALUES (?, ?)", (user_id, username))
            self.conn.commit()
            return self.get_user(user_id)
        return user

    def update_user_prime(self, user_id):
        self.conn.execute("UPDATE users SET is_prime=1 WHERE id=?", (user_id,))
        self.conn.commit()

    def add_monitor(self, user_id, url, interval):
        cursor = self.conn.cursor()
        cursor.execute("INSERT INTO monitors (user_id, url, interval) VALUES (?, ?, ?)", (user_id, url, interval))
        self.conn.commit()
        return cursor.lastrowid

    def delete_monitor(self, m_id):
        self.conn.execute("DELETE FROM monitors WHERE id=?", (m_id,))
        self.conn.execute("DELETE FROM logs WHERE monitor_id=?", (m_id,))
        self.conn.commit()

    def add_log(self, m_id, status, r_time, limit):
        self.conn.execute("INSERT INTO logs (monitor_id, status, response_time, timestamp) VALUES (?, ?, ?, ?)",
                         (m_id, status, r_time, datetime.now()))
        self.conn.execute("UPDATE monitors SET last_status=? WHERE id=?", (status, m_id))
        # Keep logs clean
        self.conn.execute(f"DELETE FROM logs WHERE monitor_id=? AND id NOT IN (SELECT id FROM logs WHERE monitor_id=? ORDER BY timestamp DESC LIMIT {limit})", (m_id, m_id))
        self.conn.commit()

db = Database()
