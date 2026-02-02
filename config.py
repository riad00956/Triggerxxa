import os

# Bot Configuration
BOT_TOKEN = os.getenv("BOT_TOKEN", "YOUR_BOT_TOKEN")
ADMIN_IDS = [int(x) for x in os.getenv("6926993789", "").split(",") if x]
PORT = int(os.getenv("PORT", 8080))

# Plan Limits
BASIC_LOGS_LIMIT = 20
PRIME_LOGS_LIMIT = 1000  # "Unlimited" practically

# Ping Intervals (Label: Seconds)
BASIC_INTERVALS = {
    "5 Min": 300,
    "15 Min": 900,
    "1 Hour": 3600
}

PRIME_INTERVALS = {
    "1 Min": 60,
    **BASIC_INTERVALS,
    "Debug (30s)": 30
}
