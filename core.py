import requests
from apscheduler.schedulers.background import BackgroundScheduler
from config import INTERVALS, PLANS

class MonitorEngine:
    def __init__(self, db, bot):
        self.db = db
        self.bot = bot
        self.scheduler = BackgroundScheduler()
        self.scheduler.start()

    def ping_task(self, monitor_id):
        monitor = self.db.conn.execute("SELECT * FROM monitors WHERE id = ?", (monitor_id,)).fetchone()
        if not monitor: return

        user = self.db.get_user(monitor['user_id'])
        limit = PLANS[user['plan']]['logs_limit']

        try:
            start_time = requests.utils.time.time()
            response = requests.get(monitor['url'], timeout=10)
            resp_time = round(requests.utils.time.time() - start_time, 2)
            status_code = response.status_code
            status = "UP" if 200 <= status_code < 400 else "DOWN"
        except Exception:
            status_code = 0
            resp_time = 0.0
            status = "DOWN"

        # Update DB
        self.db.conn.execute("UPDATE monitors SET status = ? WHERE id = ?", (status, monitor_id))
        self.db.add_log(monitor_id, status_code, resp_time, limit)

        # Notify if status changed (Logic can be expanded here)
        if monitor['status'] != status and monitor['status'] != 'Pending':
            text = f"🚨 *Alert!* \nURL: {monitor['url']}\nStatus: {status}\nCode: {status_code}"
            self.bot.send_message(monitor['user_id'], text, parse_mode="Markdown")

    def schedule_monitor(self, monitor_id, interval_label):
        seconds = INTERVALS[interval_label]
        self.scheduler.add_job(
            self.ping_task, 'interval', seconds=seconds, 
            id=f"job_{monitor_id}", args=[monitor_id], replace_existing=True
        )

    def restore_all_jobs(self):
        monitors = self.db.get_monitors()
        for m in monitors:
            self.schedule_monitor(m['id'], m['interval'])

    def stop_job(self, monitor_id):
        try: self.scheduler.remove_job(f"job_{monitor_id}")
        except: pass
