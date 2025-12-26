import os
import time
import requests

# ====== ENV VARIABLES ======
SPORTMONKS_API_KEY = os.getenv("API_KEY")
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

if not SPORTMONKS_API_KEY:
    raise ValueError("❌ SPORTMONKS_API_KEY is missing")

# ====== TELEGRAM ======
def send_message(text):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    data = {
        "chat_id": CHAT_ID,
        "text": text,
        "parse_mode": "HTML"
    }
    requests.post(url, data=data)

# ====== SPORTMONKS ======
def get_live_matches():
    url = "https://api.sportmonks.com/v3/football/livescores"
    params = {
        "api_token": SPORTMONKS_API_KEY,
        "include": "participants"
    }
    r = requests.get(url, params=params, timeout=15)
    r.raise_for_status()
    return r.json().get("data", [])

# ====== MAIN LOOP ======
send_message("🤖 البوت شغّال باستخدام SportMonks")

sent_matches = set()

while True:
    try:
        matches = get_live_matches()

        if not matches:
            time.sleep(60)
            continue

        for match in matches:
            match_id = match["id"]
            if match_id in sent_matches:
                continue

            home = away = "?"
            for team in match.get("participants", []):
                if team["meta"]["location"] == "home":
                    home = team["name"]
                elif team["meta"]["location"] == "away":
                    away = team["name"]

            msg = (
                "⚽ <b>مباراة مباشرة:</b>\n"
                f"{home} 🆚 {away}"
            )

            send_message(msg)
            sent_matches.add(match_id)

        time.sleep(60)

    except Exception as e:
        send_message(f"❌ Error: {e}")
        time.sleep(60)
