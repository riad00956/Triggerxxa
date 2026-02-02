import requests
from datetime import datetime
from apscheduler.schedulers.background import BackgroundScheduler
from database import db
from config import BASIC_LOGS_LIMIT, PRIME_LOGS_LIMIT

scheduler = BackgroundScheduler()
scheduler.start()

def ping_url(monitor_id):
    monitor = db.conn.execute("SELECT * FROM monitors WHERE id=?", (monitor_id,)).fetchone()
    if not monitor: return
    
    user = db.get_user(monitor['user_id'])
    log_limit = PRIME_LOGS_LIMIT if user['is_prime'] else BASIC_LOGS_LIMIT
    
    try:
        start = datetime.now()
        response = requests.get(monitor['url'], timeout=10)
        end = datetime.now()
        r_time = (end - start).total_seconds()
        
        status = "UP" if response.status_code == 200 else "DOWN"
        db.add_log(monitor_id, status, round(r_time, 2), log_limit)
    except Exception:
        db.add_log(monitor_id, "DOWN", 0.0, log_limit)

def setup_monitor(m_id, interval):
    scheduler.add_job(
        ping_url, 'interval', seconds=interval, 
        id=f"job_{m_id}", args=[m_id], replace_existing=True
    )

def restore_jobs():
    monitors = db.conn.execute("SELECT * FROM monitors").fetchall()
    for m in monitors:
        setup_monitor(m['id'], m['interval'])
