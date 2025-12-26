import os
import time
import requests

# ======================
# ENV VARIABLES
# ======================
SPORTMONKS_API_TOKEN = os.getenv("SPORTMONKS_API_TOKEN")
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

if not SPORTMONKS_API_TOKEN:
    raise ValueError("❌ SPORTMONKS_API_TOKEN is missing")

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
        "api_token": SPORTMONKS_API_TOKEN,
        "include": "participants;statistics"
    }
    response = requests.get(url, params=params)
    response.raise_for_status()
    return response.json()

def parse_stats(match):
    stats = match.get("statistics", [])
    home_shots = away_shots = 0

    for stat in stats:
        if stat["type"]["code"] == "shots_on_target":
            if stat["participant"]["meta"]["location"] == "home":
                home_shots = stat["data"]["value"]
            else:
                away_shots = stat["data"]["value"]

    return home_shots, away_shots

# ======================
# MAIN LOOP
# ======================
send_message("🤖 البوت شغّال باستخدام SportMonks")

while True:
    try:
        data = get_live_matches()

        for match in data.get("data", []):
            home = match["participants"][0]["name"]
            away = match["participants"][1]["name"]

            home_shots, away_shots = parse_stats(match)

            msg = (
                f"⚽ {home} vs {away}\n"
                f"🎯 تسديدات على المرمى:\n"
                f"{home}: {home_shots}\n"
                f"{away}: {away_shots}"
            )

            send_message(msg)

        time.sleep(60)

    except Exception as e:
        send_message(f"❌ Error: {e}")
        time.sleep(60)
