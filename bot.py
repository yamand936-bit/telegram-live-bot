import os
import requests
import asyncio
from telegram import Bot

# ================== ENV ==================
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

# ================== SPORTMONKS ==================
BASE_URL = "https://api.sportmonks.com/v3/football/livescores"

# ================== HELPERS ==================
def parse_stats(statistics):
    result = {
        "shots_on_target": 0,
        "shots_off_target": 0,
        "corners": 0,
        "possession": "0%"
    }

    for s in statistics:
        stat_type = s.get("type", {}).get("name")
        value = s.get("value", 0)

        if stat_type == "Shots On Target":
            result["shots_on_target"] += int(value)
        elif stat_type == "Shots Off Target":
            result["shots_off_target"] += int(value)
        elif stat_type == "Corners":
            result["corners"] += int(value)
        elif stat_type == "Ball Possession":
            result["possession"] = f"{value}%"

    return result

# ================== MAIN ==================
async def send_live_stats():
    try:
        response = requests.get(
            BASE_URL,
            params={
                "api_token": SPORTMONKS_API_KEY,
                "include": "participants;statistics"
            },
            timeout=20
        )
        response.raise_for_status()
        data = response.json().get("data", [])

        if not data:
            await bot.send_message(CHAT_ID, "⚠️ لا توجد مباريات مباشرة حالياً")
            return

        for match in data:
            teams = match.get("participants", [])
            stats = match.get("statistics", [])

            if len(teams) < 2:
                continue

            home = teams[0]["name"]
            away = teams[1]["name"]

            parsed = parse_stats(stats)

            message = (
                f"⚽ مباراة مباشرة\n"
                f"{home} 🆚 {away}\n\n"
                f"🎯 تسديدات على المرمى: {parsed['shots_on_target']}\n"
                f"❌ تسديدات خارج: {parsed['shots_off_target']}\n"
                f"🚩 ركنيات: {parsed['corners']}\n"
                f"📊 استحواذ: {parsed['possession']}"
            )

            await bot.send_message(CHAT_ID, message)

    except Exception as e:
        await bot.send_message(CHAT_ID, f"❌ Error: {e}")

# ================== RUN ==================
if __name__ == "__main__":
    asyncio.run(send_live_stats())
