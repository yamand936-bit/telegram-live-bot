import requests
import time
import os

# ================== ENV ==================
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")
SPORTMONKS_TOKEN = os.getenv("SPORTMONKS_TOKEN")

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

def get_stat(stats, name):
    for s in stats:
        if s["type"]["name"] == name:
            return s["value"]
    return 0

# ================== START ==================
send_message("🤖 البوت شغّال باستخدام SportMonks")

sent = set()

while True:
    try:
        matches = get_live_matches()

        for match in matches:
            match_id = match["id"]
            if match_id in sent:
                continue

            home = match["participants"][0]["name"]
            away = match["participants"][1]["name"]
            minute = match["time"]["minute"]

            home_stats = match["statistics"]["home"]
            away_stats = match["statistics"]["away"]

            hs = get_stat(home_stats, "Shots On Target")
            as_ = get_stat(away_stats, "Shots On Target")

            msg = (
                f"⚽ LIVE\n"
                f"{home} vs {away}\n"
                f"⏱ {minute}'\n"
                f"🎯 تسديدات على المرمى:\n"
                f"{home}: {hs}\n"
                f"{away}: {as_}"
            )

            send_message(msg)
            sent.add(match_id)

        time.sleep(60)

    except Exception as e:
        send_message(f"❌ Error: {e}")
        time.sleep(60)
