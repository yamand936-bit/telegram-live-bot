import requests
import time
import os

# ================== ENV ==================
TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN")
CHAT_ID = os.environ.get("CHAT_ID")
SPORTMONKS_TOKEN = os.environ.get("SPORTMONKS_TOKEN")

BASE_URL = "https://api.sportmonks.com/v3/football"

# ================== FUNCTIONS ==================
def send_message(text):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    requests.post(url, data={
        "chat_id": CHAT_ID,
        "text": text
    })

def get_live_matches():
    url = f"{BASE_URL}/fixtures/live"
    params = {
        "api_token": SPORTMONKS_TOKEN,
        "include": "league;participants;statistics"
    }
    r = requests.get(url, params=params)
    return r.json().get("data", [])

def get_stat(stats, name):
    for s in stats:
        if s["type"]["name"].lower() == name.lower():
            return s["data"]["value"]
    return 0

# ================== START ==================
send_message("🤖 البوت شغّال باستخدام SportMonks")

last_state = {}

while True:
    matches = get_live_matches()
    blocks = []

    for m in matches:
        league = m["league"]["name"]

        home = m["participants"][0]["name"]
        away = m["participants"][1]["name"]

        minute = m["time"]["minute"]

        stats = m.get("statistics", [])

        home_goals = get_stat(stats, "Goals")
        away_goals = get_stat(stats, "Goals")

        home_shots = get_stat(stats, "Shots On Target")
        away_shots = get_stat(stats, "Shots On Target")

        state = f"{home_goals}-{away_goals}-{home_shots}-{away_shots}"
        if last_state.get(m["id"]) == state:
            continue

        last_state[m["id"]] = state

        block = (
            f"⚽ {league}\n"
            f"{home} vs {away}\n"
            f"⏱ {minute}'\n"
            f"🔢 {home_goals} - {away_goals}\n"
            f"🎯 تسديدات على المرمى:\n"
            f"🥅 {home}: {home_shots}\n"
            f"🥅 {away}: {away_shots}\n"
        )

        blocks.append(block)

    if blocks:
        send_message("📊 تحديث المباريات المباشرة\n\n" + "\n".join(blocks))

    time.sleep(60)
