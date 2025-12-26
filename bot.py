import os
import requests
import asyncio
from telegram import Bot

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

BASE_URL = "https://api.sportmonks.com/v3/football"

def get_live_matches():
    url = f"{BASE_URL}/livescores"
    params = {
        "api_token": SPORTMONKS_API_KEY,
        "include": "participants;statistics.type"
    }
    r = requests.get(url, params=params, timeout=20)
    r.raise_for_status()
    return r.json().get("data", [])

def parse_statistics(stats):
    data = {
        "shots_on_target": 0,
        "shots_off_target": 0,
        "corners": 0,
        "possession": 0
    }

    for s in stats:
        stat_type = s.get("type", {}).get("name", "").lower()
        value = s.get("value", 0)

        if "shots on target" in stat_type:
            data["shots_on_target"] += int(value)
        elif "shots off target" in stat_type:
            data["shots_off_target"] += int(value)
        elif "corner" in stat_type:
            data["corners"] += int(value)
        elif "possession" in stat_type:
            try:
                data["possession"] = int(float(value))
            except:
                pass

    return data

async def send_live_stats():
    matches = get_live_matches()

    if not matches:
        await bot.send_message(chat_id=CHAT_ID, text="⚽ لا توجد مباريات مباشرة حالياً")
        return

    for match in matches:
        teams = match.get("participants", [])
        home = teams[0]["name"] if len(teams) > 0 else "?"
        away = teams[1]["name"] if len(teams) > 1 else "?"

        stats = parse_statistics(match.get("statistics", []))

        message = (
            f"⚽ مباراة مباشرة\n"
            f"{home} 🆚 {away}\n\n"
            f"🎯 تسديدات على المرمى: {stats['shots_on_target']}\n"
            f"❌ تسديدات خارج: {stats['shots_off_target']}\n"
            f"🚩 ركنيات: {stats['corners']}\n"
            f"📊 استحواذ: {stats['possession']}%\n"
        )

        await bot.send_message(chat_id=CHAT_ID, text=message)

async def main():
    await bot.send_message(chat_id=CHAT_ID, text="🤖 البوت يعمل مع إحصائيات SportMonks")
    await send_live_stats()

if __name__ == "__main__":
    asyncio.run(main())
