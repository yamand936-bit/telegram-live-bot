import requests
import time
import os

# ================= ENV =================
TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN")
CHAT_ID = os.environ.get("CHAT_ID")
SPORTMONKS_TOKEN = os.environ.get("SPORTMONKS_TOKEN")

BASE_URL = "https://api.sportmonks.com/v3/football"

# ================= TELEGRAM =================
def send_message(text):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    requests.post(url, data={"chat_id": CHAT_ID, "text": text})

# ================= LIVE MATCHES =================
def get_live_matches():
    url = f"{BASE_URL}/fixtures/live"
    params = {
        "api_token": SPORTMONKS_TOKEN,
        "include": "participants;statistics.type"
    }
    r = requests.get(url, params=params, timeout=20)
    return r.json().get("data", [])

# ================= SHOTS ON TARGET =================
def shots_on_target(stats, team_id):
    for s in stats:
        if s["type"]["name"] == "Shots On Target" and s["participant_id"] == team_id:
            return s["data"]["value"]
    return 0

# ================= START =================
send_message("🤖 البوت شغّال باستخدام SportMonks")

last_state = {}

while True:
    try:
        matches = get_live_matches()

        for m in matches:
            fixture_id = m["id"]
            minute = m["time"]["minute"]

            home = m["participants"][0]
            away = m["participants"][1]

            home_name = home["name"]
            away_name = away["name"]

            gh = m["scores"]["localteam_score"]
            ga = m["scores"]["visitorteam_score"]

            stats = m.get("statistics", [])

            hs = shots_on_target(stats, home["id"])
            ass = shots_on_target(stats, away["id"])

            state = f"{gh}-{ga}-{hs}-{ass}"
            if last_state.get(fixture_id) == state:
                continue

            last_state[fixture_id] = state

            msg = (
                f"⚽ {home_name} vs {away_name}\n"
                f"⏱ {minute}'\n"
                f"🔢 {gh} - {ga}\n"
                f"🎯 تسديدات على المرمى:\n"
                f"{home_name}: {hs}\n"
                f"{away_name}: {ass}"
            )

            send_message(msg)

        time.sleep(60)

    except Exception as e:
        print("ERROR:", e)
        time.sleep(60)
