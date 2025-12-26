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
    requests.post(url, data={"chat_id": CHAT_ID, "text": text})


def get_live_matches():
    url = f"{BASE_URL}/fixtures"
    params = {
        "api_token": SPORTMONKS_TOKEN,
        "include": "statistics;participants;league",
        "filter[status]": "inplay"
    }
    r = requests.get(url, params=params)
    return r.json().get("data", [])


def get_stat(stats, name):
    for s in stats:
        if s["type"]["name"] == name:
            return s["value"]
    return "?"


# ================== START ==================
send_message("🤖 البوت شغّال باستخدام SportMonks")

last_state = {}

while True:
    matches = get_live_matches()
    messages = []

    for match in matches:
        fixture_id = match["id"]
        league = match["league"]["name"]

        home = match["participants"][0]["name"]
        away = match["participants"][1]["name"]

        minute = match["time"]["minute"]

        score_home = match["scores"]["localteam_score"]
        score_away = match["scores"]["visitorteam_score"]

        stats = match.get("statistics", [])

        home_shots = get_stat(stats, "Shots On Target - Home")
        away_shots = get_stat(stats, "Shots On Target - Away")

        state = f"{score_home}-{score_away}-{home_shots}-{away_shots}"
        if last_state.get(fixture_id) == state:
            continue

        last_state[fixture_id] = state

        msg = (
            f"⚽ {league}\n"
            f"{home} vs {away}\n"
            f"⏱ {minute}'\n"
            f"🔢 {score_home} - {score_away}\n"
            f"🎯 تسديدات على المرمى:\n"
            f"{home}: {home_shots}\n"
            f"{away}: {away_shots}\n"
        )

        messages.append(msg)

    if messages:
        send_message("📊 تحديث المباريات المباشرة\n\n" + "\n".join(messages))

    time.sleep(60)
