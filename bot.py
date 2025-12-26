import requests
import time
import os

# ============ ENV ============
TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN")
CHAT_ID = os.environ.get("CHAT_ID")
SPORTMONKS_TOKEN = os.environ.get("SPORTMONKS_TOKEN")

BASE_URL = "https://api.sportmonks.com/v3/football"

HEADERS = {
    "Authorization": f"Bearer {SPORTMONKS_TOKEN}"
}

# ============ FUNCTIONS ============
def send_message(text):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    requests.post(url, data={"chat_id": CHAT_ID, "text": text})


def get_live_matches():
    url = f"{BASE_URL}/fixtures"
    params = {
        "include": "participants;statistics",
        "filters": "state_id:2"  # LIVE ONLY
    }
    r = requests.get(url, headers=HEADERS, params=params)
    return r.json().get("data", [])


def get_shots(stats, team_id):
    for stat in stats:
        if stat["type"]["name"] == "Shots On Target" and stat["participant_id"] == team_id:
            return stat["value"]
    return "?"


# ============ START ============
send_message("🤖 البوت شغّال باستخدام SportMonks")

last_sent = {}

while True:
    try:
        matches = get_live_matches()

        for m in matches:
            fixture_id = m["id"]

            home = m["participants"][0]["name"]
            away = m["participants"][1]["name"]

            home_id = m["participants"][0]["id"]
            away_id = m["participants"][1]["id"]

            minute = m["time"]["minute"] if m.get("time") else "?"

            stats = m.get("statistics", [])

            hs = get_shots(stats, home_id)
            as_ = get_shots(stats, away_id)

            state = f"{hs}-{as_}-{minute}"
            if last_sent.get(fixture_id) == state:
                continue

            last_sent[fixture_id] = state

            msg = (
                f"⚽ LIVE\n"
                f"{home} vs {away}\n"
                f"⏱ {minute}'\n"
                f"🎯 تسديدات على المرمى:\n"
                f"{home}: {hs}\n"
                f"{away}: {as_}"
            )

            send_message(msg)

    except Exception as e:
        send_message(f"❌ Error: {e}")

    time.sleep(60)
