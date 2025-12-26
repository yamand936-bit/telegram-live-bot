import os
import time
import requests

# ======================
# ENV VARIABLES
# ======================
SPORTMONKS_API_KEY = os.getenv("SPORTMONKS_API_KEY")
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

if not SPORTMONKS_API_KEY:
    raise ValueError("❌ SPORTMONKS_API_KEY is missing")

# ======================
# TELEGRAM
# ======================
def send_message(text):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    data = {
        "chat_id": CHAT_ID,
        "text": text
    }
    requests.post(url, data=data)

# ======================
# SPORTMONKS
# ======================
def get_live_matches():
    url = "https://api.sportmonks.com/v3/football/livescores"
    params = {
        "api_token": SPORTMONKS_API_KEY,
        "include": "participants"
    }
    response = requests.get(url, params=params, timeout=20)
    response.raise_for_status()
    return response.json()

# ======================
# MAIN LOOP
# ======================
send_message("🤖 البوت شغّال باستخدام SportMonks")

while True:
    try:
        data = get_live_matches()
        matches = data.get("data", [])

        if not matches:
            send_message("⏳ لا توجد مباريات حالياً")
        else:
            for match in matches:
                home = match["participants"][0]["name"]
                away = match["participants"][1]["name"]
                send_message(f"⚽ مباراة مباشرة:\n{home} 🆚 {away}")

    except Exception as e:
        send_message(f"❌ Error: {e}")

    time.sleep(60)
