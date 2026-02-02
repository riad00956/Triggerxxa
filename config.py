import os

# Bot Configuration
BOT_TOKEN = os.getenv("BOT_TOKEN", "YOUR_BOT_TOKEN_HERE")
ADMIN_IDS = [int(x) for x in os.getenv("ADMIN_IDS", "6926993789").split(",") if x]

# Plan Settings
PLANS = {
    "BASIC": {"logs_limit": 20, "label": "🟢 BASIC"},
    "PRIME": {"logs_limit": 1000, "label": "💎 PRIME"}
}

# Monitoring Settings
INTERVALS = {
    "1m": 60,
    "5m": 300,
    "15m": 900,
    "1h": 3600
}

DATABASE_NAME = "uptime.db"
