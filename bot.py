import os
import time
import requests

# ================== ENV VARIABLES ==================
API_KEY = os.getenv("API_KEY")
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

# ================== TELEGRAM ==================
def send_message(text):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {
        "chat_id": CHAT_ID,
        "text": text,
        "parse_mode": "HTML"
    }
    requests.post(url, json=payload)

# ================== SPORTMONKS ==================
def get_live_matches():
    url = "https://api.sportmonks.com/v3/football/livescores"
    params = {
        "api_token": API_KEY,
        "include": "participants;statistics"
    }
    response = requests.get(url, params=params, timeout=30)
    response.raise_for_status()
    return response.json().get("data", [])

def get_shots_on_target(stats, team_id):
    for stat in stats:
        if stat["team_id"] == team_id and stat["type"]["name"] == "Shots On Target":
            return stat["value"]
    return 0

# ================== MAIN LOOP ==================
send_message("🤖 البوت شغّال باستخدام SportMonks")

while True:
    try:
        matches = get_live_matches()

        if not matches:
            time.sleep(60)
            continue

        for match in matches:
            if "statistics" not in match or not match["statistics"]:
                continue

            home = match["participants"][0]
            away = match["participants"][1]

            home_sot = get_shots_on_target(match["statistics"], home["id"])
            away_sot = get_shots_on_target(match["statistics"], away["id"])

            message = (
                f"🏟 <b>{home['name']} vs {away['name']}</b>\n"
                f"🎯 تسديدات على المرمى:\n"
                f"🔵 {home['name']}: {home_sot}\n"
                f"🔴 {away['name']}: {away_sot}"
            )

            send_message(message)

        time.sleep(60)

    except Exception as e:
        send_message(f"❌ Error: {str(e)}")
        time.sleep(60)
