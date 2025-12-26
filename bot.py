import os
import requests
import time

# ================== ENV VARIABLES ==================
SPORTMONKS_API_KEY = os.getenv("SPORTMONKS_API_KEY")
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

if not SPORTMONKS_API_KEY:
    raise ValueError("❌ SPORTMONKS_API_KEY is missing")

# ================== TELEGRAM ==================
def send_telegram(message):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {
        "chat_id": CHAT_ID,
        "text": message,
        "parse_mode": "HTML"
    }
    requests.post(url, json=payload)

# ================== SPORTMONKS ==================
def get_live_matches():
    url = "https://api.sportmonks.com/v3/football/livescores"
    params = {
        "api_token": SPORTMONKS_API_KEY,
        "include": "participants;statistics"
    }
    r = requests.get(url, params=params, timeout=20)
    r.raise_for_status()
    return r.json().get("data", [])

def extract_stat(stats, name):
    for s in stats:
        if s.get("type", {}).get("name") == name:
            return s.get("value", 0)
    return 0

# ================== MAIN LOOP ==================
send_telegram("🤖 البوت شغّال باستخدام SportMonks (Advanced Plan)")

while True:
    try:
        matches = get_live_matches()

        if not matches:
            time.sleep(60)
            continue

        for match in matches:
            home = match["participants"][0]["name"]
            away = match["participants"][1]["name"]

            stats = match.get("statistics", [])

            shots_on = extract_stat(stats, "Shots On Target")
            shots_off = extract_stat(stats, "Shots Off Target")
            corners = extract_stat(stats, "Corners")
            possession = extract_stat(stats, "Ball Possession")

            message = (
                f"⚽ <b>مباراة مباشرة</b>\n\n"
                f"{home} 🆚 {away}\n\n"
                f"🎯 تسديدات على المرمى: {shots_on}\n"
                f"❌ تسديدات خارج: {shots_off}\n"
                f"🚩 ركنيات: {corners}\n"
                f"📊 استحواذ: {possession}%"
            )

            send_telegram(message)
            time.sleep(5)

        time.sleep(60)

    except Exception as e:
        send_telegram(f"❌ Error: {e}")
        time.sleep(60)
