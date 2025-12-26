import os
import requests
import time

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")
SPORTMONKS_API_KEY = os.getenv("SPORTMONKS_API_KEY")

if not SPORTMONKS_API_KEY:
    raise ValueError("❌ SPORTMONKS_API_KEY is missing")

BASE_URL = "https://api.sportmonks.com/v3/football/livescores"

def send_message(text):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    requests.post(url, data={
        "chat_id": CHAT_ID,
        "text": text
    })

def get_live_matches():
    params = {
        "api_token": SPORTMONKS_API_KEY,
        "include": "participants"
    }
    r = requests.get(BASE_URL, params=params, timeout=20)
    r.raise_for_status()
    return r.json().get("data", [])

send_message("🤖 البوت شغّال باستخدام SportMonks")

while True:
    try:
        matches = get_live_matches()

        if not matches:
            time.sleep(60)
            continue

        for m in matches:
            home = m["participants"][0]["name"]
            away = m["participants"][1]["name"]
            send_message(f"⚽ مباراة مباشرة:\n{home} 🆚 {away}")

        time.sleep(120)

    except Exception as e:
        send_message(f"❌ Error: {e}")
        time.sleep(120)
