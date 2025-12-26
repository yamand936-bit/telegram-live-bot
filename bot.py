import os
import requests
import time
from telegram import Bot

# =========================
# Environment Variables
# =========================
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")
SPORTMONKS_API_KEY = os.getenv("SPORTMONKS_API_KEY")

if not TELEGRAM_TOKEN:
    raise ValueError("❌ TELEGRAM_TOKEN is missing")

if not CHAT_ID:
    raise ValueError("❌ CHAT_ID is missing")

if not SPORTMONKS_API_KEY:
    raise ValueError("❌ SPORTMONKS_API_KEY is missing")

bot = Bot(token=TELEGRAM_TOKEN)

# =========================
# SportMonks API
# =========================
BASE_URL = "https://api.sportmonks.com/v3/football"

def get_live_matches():
    url = f"{BASE_URL}/livescores"
    params = {
        "api_token": SPORTMONKS_API_KEY,
        "include": "participants;statistics"
    }
    r = requests.get(url, params=params, timeout=20)
    r.raise_for_status()
    return r.json().get("data", [])

def extract_stats(stats):
    data = {
        "shots_on_target": 0,
        "shots_off_target": 0,
        "corners": 0,
        "possession": 0
    }

    if not stats:
        return data

    for s in stats:
        name = s.get("type", {}).get("name", "").lower()
        value = s.get("value", 0)

        if "shots on target" in name:
            data["shots_on_target"] += int(value)
        elif "shots off target" in name:
            data["shots_off_target"] += int(value)
        elif "corners" in name:
            data["corners"] += int(value)
        elif "ball possession" in name:
            data["possession"] = int(value)

    return data

def send_live_matches():
    matches = get_live_matches()

    if not matches:
        bot.send_message(chat_id=CHAT_ID, text="⚽ لا توجد مباريات مباشرة حالياً")
        return

    for match in matches:
        teams = match.get("participants", [])
        home = teams[0]["name"] if len(teams) > 0 else "Home"
        away = teams[1]["name"] if len(teams) > 1 else "Away"

        stats = extract_stats(match.get("statistics", []))

        message = (
            f"⚽ مباراة مباشرة\n\n"
            f"{home} 🆚 {away}\n\n"
            f"🎯 تسديدات على المرمى: {stats['shots_on_target']}\n"
            f"❌ تسديدات خارج: {stats['shots_off_target']}\n"
            f"🚩 ركنيات: {stats['corners']}\n"
            f"📊 استحواذ: {stats['possession']}%\n"
        )

        bot.send_message(chat_id=CHAT_ID, text=message)

# =========================
# Main Loop
# =========================
bot.send_message(chat_id=CHAT_ID, text="🤖 البوت شغّال مع إحصائيات SportMonks")

while True:
    try:
        send_live_matches()
    except Exception as e:
        bot.send_message(chat_id=CHAT_ID, text=f"❌ Error: {e}")
    time.sleep(120)
