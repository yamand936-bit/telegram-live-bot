import os
import time
import requests

# ====== ENV VARIABLES ======
SPORTMONKS_API_KEY = os.getenv("SPORTMONKS_API_KEY")
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

# ====== CHECK ======
if not SPORTMONKS_API_KEY:
    raise ValueError("❌ SPORTMONKS_API_KEY is missing")

# ====== TELEGRAM ======
def send_message(text):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {
        "chat_id": CHAT_ID,
        "text": text,
        "parse_mode": "HTML"
    }
    requests.post(url, json=payload)

# ====== SPORTMONKS ======
def get_live_matches():
    url = "https://api.sportmonks.com/v3/football/livescores"
    params = {
        "api_token": SPORTMONKS_API_KEY,
        "include": "participants;statistics"
    }
    response = requests.get(url, params=params)
    response.raise_for_status()
    return response.json()["data"]

# ====== FORMAT ======
def format_match(match):
    home = match["participants"][0]["name"]
    away = match["participants"][1]["name"]

    stats = match.get("statistics", [])
    shots_home = shots_away = "?"

    for s in stats:
        if s["type"]["name"] == "Shots On Target":
            if s["participant_id"] == match["participants"][0]["id"]:
                shots_home = s["data"]["value"]
            else:
                shots_away = s["data"]["value"]

    return (
        f"⚽ <b>{home} vs {away}</b>\n"
        f"🎯 تسديدات على المرمى:\n"
        f"{home}: {shots_home}\n"
        f"{away}: {shots_away}"
    )

# ====== MAIN LOOP ======
send_message("🤖 البوت شغّال باستخدام SportMonks")

while True:
    try:
        matches = get_live_matches()

        if not matches:
            send_message("⏸️ لا توجد مباريات مباشرة الآن")
        else:
            for match in matches:
                send_message(format_match(match))

    except Exception as e:
        send_message(f"❌ Error: {e}")

    time.sleep(60)
