import os
import requests
from telegram import Bot
from telegram.constants import ParseMode

# ================= ENV =================
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")
SPORTMONKS_API_KEY = os.getenv("SPORTMONKS_API_KEY")

if not TELEGRAM_TOKEN or not CHAT_ID or not SPORTMONKS_API_KEY:
    raise ValueError("❌ Missing environment variables")

bot = Bot(token=TELEGRAM_TOKEN)

BASE_URL = "https://api.sportmonks.com/v3/football"

# ================= HELPERS =================
def get_live_matches():
    url = f"{BASE_URL}/livescores"
    params = {
        "api_token": SPORTMONKS_API_KEY,
        "include": "participants;statistics"
    }
    r = requests.get(url, params=params, timeout=20)
    r.raise_for_status()
    return r.json().get("data", [])


def parse_stats(stats):
    data = {
        "shots_on": 0,
        "shots_off": 0,
        "corners": 0,
        "possession": 0
    }

    for s in stats:
        if s["type"]["name"] == "Shots On Target":
            data["shots_on"] = s["value"]
        elif s["type"]["name"] == "Shots Off Target":
            data["shots_off"] = s["value"]
        elif s["type"]["name"] == "Corners":
            data["corners"] = s["value"]
        elif s["type"]["name"] == "Ball Possession":
            data["possession"] = s["value"]

    return data


# ================= MAIN =================
def send_live_stats():
    matches = get_live_matches()

    if not matches:
        bot.send_message(chat_id=CHAT_ID, text="⚽ لا توجد مباريات مباشرة حالياً")
        return

    for match in matches:
        home = match["participants"][0]["name"]
        away = match["participants"][1]["name"]

        stats = parse_stats(match.get("statistics", []))

        message = f"""
⚽ **مباراة مباشرة**
{home} 🆚 {away}

🎯 تسديدات على المرمى: {stats['shots_on']}
❌ تسديدات خارج: {stats['shots_off']}
🚩 ركنيات: {stats['corners']}
📊 استحواذ: {stats['possession']}%
"""

        bot.send_message(
            chat_id=CHAT_ID,
            text=message,
            parse_mode=ParseMode.MARKDOWN
        )


if __name__ == "__main__":
    bot.send_message(chat_id=CHAT_ID, text="🤖 البوت شغّال باستخدام SportMonks (إحصائيات)")
    send_live_stats()
