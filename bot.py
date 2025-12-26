import os
import requests
import asyncio
from telegram import Bot

# ===== ENV =====
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")
SPORTMONKS_API_KEY = os.getenv("SPORTMONKS_API_KEY")

if not TELEGRAM_TOKEN or not CHAT_ID or not SPORTMONKS_API_KEY:
    raise ValueError("❌ Missing environment variables")

bot = Bot(token=TELEGRAM_TOKEN)

# ===== SPORTMONKS =====
BASE_URL = "https://api.sportmonks.com/v3/football/livescores"

STAT_NAMES = {
    "Shots On Target": "🎯 تسديدات على المرمى",
    "Shots Off Target": "❌ تسديدات خارج",
    "Corners": "🚩 ركنيات",
    "Ball Possession": "📊 استحواذ"
}


def fetch_live_matches():
    params = {
        "api_token": SPORTMONKS_API_KEY,
        "include": "participants;statistics"
    }
    r = requests.get(BASE_URL, params=params, timeout=20)
    r.raise_for_status()
    return r.json().get("data", [])


def parse_stats(statistics):
    result = {
        "🎯 تسديدات على المرمى": 0,
        "❌ تسديدات خارج": 0,
        "🚩 ركنيات": 0,
        "📊 استحواذ": "0%"
    }

    for s in statistics:
        stat_type = s.get("type", {})
        name = stat_type.get("name")

        if not name:
            continue

        if name in STAT_NAMES:
            label = STAT_NAMES[name]
            value = s.get("value", 0)

            if name == "Ball Possession":
                result[label] = f"{value}%"
            else:
                result[label] += int(value)

    return result


async def send_live_stats():
    matches = fetch_live_matches()

    if not matches:
        await bot.send_message(chat_id=CHAT_ID, text="❌ لا توجد مباريات مباشرة حالياً")
        return

    for match in matches:
        teams = match.get("participants", [])
        home = teams[0]["name"] if len(teams) > 0 else "?"
        away = teams[1]["name"] if len(teams) > 1 else "?"

        stats = parse_stats(match.get("statistics", []))

        message = f"""⚽ مباراة مباشرة
{home} 🆚 {away}

{stats["🎯 تسديدات على المرمى"]}
{stats["❌ تسديدات خارج"]}
{stats["🚩 ركنيات"]}
{stats["📊 استحواذ"]}
"""
        await bot.send_message(chat_id=CHAT_ID, text=message)


# ===== RUN =====
if __name__ == "__main__":
    asyncio.run(send_live_stats())
