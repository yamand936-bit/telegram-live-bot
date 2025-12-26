import os
import requests
import asyncio
from telegram import Bot

TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")
API_KEY = os.getenv("SPORTMONKS_API_KEY")

bot = Bot(token=TOKEN)

BASE_URL = "https://api.sportmonks.com/v3/football/livescores"

def fetch_live_matches():
    params = {
        "api_token": API_KEY,
        "include": "participants;statistics"
    }
    r = requests.get(BASE_URL, params=params, timeout=30)
    r.raise_for_status()
    return r.json()["data"]

def parse_stats(statistics):
    stats = {
        "shots_on_target": 0,
        "shots_off_target": 0,
        "corners": 0,
        "possession": 0
    }

    possession_values = []

    for s in statistics:
        code = s["type"]["code"]
        value = s.get("value", 0)

        if code == "shots_on_target":
            stats["shots_on_target"] += value
        elif code == "shots_off_target":
            stats["shots_off_target"] += value
        elif code == "corners":
            stats["corners"] += value
        elif code == "ball_possession":
            possession_values.append(value)

    if possession_values:
        stats["possession"] = round(sum(possession_values) / len(possession_values))

    return stats

async def send_live_stats():
    matches = fetch_live_matches()

    for match in matches:
        home = match["participants"][0]["name"]
        away = match["participants"][1]["name"]
        statistics = match.get("statistics", [])

        stats = parse_stats(statistics)

        message = (
            f"⚽ مباراة مباشرة\n"
            f"{home} 🆚 {away}\n\n"
            f"🎯 تسديدات على المرمى: {stats['shots_on_target']}\n"
            f"❌ تسديدات خارج: {stats['shots_off_target']}\n"
            f"🚩 ركنيات: {stats['corners']}\n"
            f"📊 استحواذ: {stats['possession']}%"
        )

        await bot.send_message(chat_id=CHAT_ID, text=message)

async def main():
    await bot.send_message(chat_id=CHAT_ID, text="🤖 البوت يعمل مع إحصائيات SportMonks")
    while True:
        await send_live_stats()
        await asyncio.sleep(60)

if __name__ == "__main__":
    asyncio.run(main())
