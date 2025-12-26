import requests
import time
import os

# ================== ENV ==================
TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN")
CHAT_ID = os.environ.get("CHAT_ID")
SPORTMONKS_TOKEN = os.environ.get("SPORTMONKS_TOKEN")

BASE_URL = "https://api.sportmonks.com/v3/football"

# ================== TELEGRAM ==================
def send_message(text):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    requests.post(url, data={"chat_id": CHAT_ID, "text": text})

# ================== SPORTMONKS ==================
def get_live_matches():
    url = f"{BASE_URL}/livescores"
    params = {
        "api_token": SPORTMONKS_TOKEN,
        "include": "participants;statistics"
    }
    r = requests.get(url, params=params, timeout=20)
    r.raise_for_status()
    return r.json()["data"]

def shots_on_target(stats, team_id):
    for s in stats:
        if s["team_id"] == team_id and s["type"]["name"] == "Shots On Target":
            return s["value"]
    return "?"

# ================== START ==================
send_message("🤖 البوت شغّال باستخدام SportMonks")

last_sent = {}

while True:
    try:
        matches = get_live_matches()

        for match in matches:
            fixture_id = match["id"]
            league = match["league"]["name"]

            home = match["participants"][0]
            away = match["participants"][1]

            gh = match["scores"]["localteam_score"]
            ga = match["scores"]["visitorteam_score"]

            minute = match["time"]["minute"]

            hs = shots_on_target(match["statistics"], home["id"])
            as_ = shots_on_target(match["statistics"], away["id"])

            state = f"{gh}-{ga}-{hs}-{as_}"
            if last_sent.get(fixture_id) == state:
                continue

            last_sent[fixture_id] = state

            msg = (
                f"⚽ {league}\n"
                f"{home['name']} vs {away['name']}\n"
                f"⏱ {minute}'\n"
                f"🔢 {gh} - {ga}\n"
                f"🎯 تسديدات على المرمى:\n"
                f"{home['name']}: {hs}\n"
                f"{away['name']}: {as_}"
            )

            send_message(msg)

    except Exception as e:
        send_message(f"❌ Error: {e}")

    time.sleep(60)
