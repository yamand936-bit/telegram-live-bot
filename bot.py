import os
import time
import requests

# ======================
# Environment Variables
# ======================
SPORTMONKS_API_KEY = os.getenv("API_KEY")
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

# ======================
# Telegram Function
# ======================
def send_message(text):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    data = {
        "chat_id": CHAT_ID,
        "text": text
    }
    requests.post(url, data=data)

# ======================
# SportMonks Live Matches
# ======================
def get_live_matches():
    url = "https://api.sportmonks.com/v3/football/livescores"

    params = {
        "api_token": SPORTMONKS_API_KEY,
        "include": "participants;statistics"
    }

    response = requests.get(url, params=params)
    response.raise_for_status()
    return response.json()

# ======================
# Main Loop
# ======================
send_message("🤖 البوت شغّال باستخدام SportMonks")

while True:
    try:
        data = get_live_matches()

        matches = data.get("data", [])
        if not matches:
            time.sleep(60)
            continue

        for match in matches:
            name = match.get("name", "مباراة")
            stats = match.get("statistics", [])

            shots_on_target = 0
            for stat in stats:
                if stat.get("type", {}).get("name") == "Shots On Target":
                    shots_on_target = stat.get("total", 0)

            message = f"""
⚽ {name}
🎯 تسديدات على المرمى: {shots_on_target}
"""
            send_message(message)

        time.sleep(60)

    except Exception as e:
        send_message(f"❌ Error: {e}")
        time.sleep(60)
