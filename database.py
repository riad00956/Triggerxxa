import sqlite3
from datetime import datetime

class Database:
    def __init__(self, db_name):
        self.conn = sqlite3.connect(db_name, check_same_thread=False)
        self.conn.row_factory = sqlite3.Row
        self.create_tables()

    def create_tables(self):
        cursor = self.conn.cursor()
        cursor.execute('''CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY, plan TEXT DEFAULT 'BASIC', joined_at TIMESTAMP)''')
        cursor.execute('''CREATE TABLE IF NOT EXISTS monitors (
            id INTEGER PRIMARY KEY AUTOINCREMENT, user_id INTEGER, 
            url TEXT, interval TEXT, status TEXT DEFAULT 'Pending')''')
        cursor.execute('''CREATE TABLE IF NOT EXISTS logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT, monitor_id INTEGER, 
            status_code INTEGER, response_time REAL, timestamp TIMESTAMP)''')
        cursor.execute('''CREATE TABLE IF NOT EXISTS keys (
            key_code TEXT PRIMARY KEY, is_used INTEGER DEFAULT 0, redeemed_by INTEGER)''')
        self.conn.commit()

    def get_user(self, user_id):
        user = self.conn.execute("SELECT * FROM users WHERE user_id = ?", (user_id,)).fetchone()
        if not user:
            self.conn.execute("INSERT INTO users (user_id, joined_at) VALUES (?, ?)", 
                             (user_id, datetime.now()))
            self.conn.commit()
            return self.get_user(user_id)
        return user

    def update_user_plan(self, user_id, plan):
        self.conn.execute("UPDATE users SET plan = ? WHERE user_id = ?", (plan, user_id))
        self.conn.commit()

    def add_monitor(self, user_id, url, interval):
        cursor = self.conn.cursor()
        cursor.execute("INSERT INTO monitors (user_id, url, interval) VALUES (?, ?, ?)", (user_id, url, interval))
        self.conn.commit()
        return cursor.lastrowid

    def delete_monitor(self, monitor_id):
        self.conn.execute("DELETE FROM monitors WHERE id = ?", (monitor_id,))
        self.conn.execute("DELETE FROM logs WHERE monitor_id = ?", (monitor_id,))
        self.conn.commit()

    def get_monitors(self, user_id=None):
        if user_id:
            return self.conn.execute("SELECT * FROM monitors WHERE user_id = ?", (user_id,)).fetchall()
        return self.conn.execute("SELECT * FROM monitors").fetchall()

    def add_log(self, monitor_id, status_code, response_time, limit):
        self.conn.execute("INSERT INTO logs (monitor_id, status_code, response_time, timestamp) VALUES (?, ?, ?, ?)",
                         (monitor_id, status_code, response_time, datetime.now()))
        # Keep logs within limit
        self.conn.execute("DELETE FROM logs WHERE monitor_id = ? AND id NOT IN (SELECT id FROM logs WHERE monitor_id = ? ORDER BY timestamp DESC LIMIT ?)",
                         (monitor_id, monitor_id, limit))
        self.conn.commit()

    def get_logs(self, monitor_id):
        return self.conn.execute("SELECT * FROM logs WHERE monitor_id = ? ORDER BY timestamp DESC", (monitor_id,)).fetchall()

    def create_key(self, key_code):
        self.conn.execute("INSERT INTO keys (key_code) VALUES (?)", (key_code,))
        self.conn.commit()

    def use_key(self, key_code, user_id):
        key = self.conn.execute("SELECT * FROM keys WHERE key_code = ? AND is_used = 0", (key_code,)).fetchone()
        if key:
            self.conn.execute("UPDATE keys SET is_used = 1, redeemed_by = ? WHERE key_code = ?", (user_id, key_code))
            self.conn.commit()
            return True
        return False
