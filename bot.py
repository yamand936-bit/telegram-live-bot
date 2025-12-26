import os
import requests
import asyncio
from telegram import Bot

# ================== CONFIG ==================
API_KEY = os.getenv("SPORTMONKS_API_KEY")
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

LEAGUE_ID = 550  # 🇹🇷 Turkish 1. Lig
BASE_URL = "https://api.sportmonks.com/v3/football"

bot = Bot(token=TELEGRAM_TOKEN)

# ================== HELPERS ==================
def get_live_matches():
    url = f"{BASE_URL}/livescores"
    params = {
        "api_token": API_KEY,
        "include": "participants;statistics",
        "filters[league_id]": LEAGUE_ID
    }
    r = requests.get(url, params=params, timeout=20)
    r.raise_for_status()
    return r.json().get("data", [])

def parse_statistics(stats):
    data = {
        "shots_on": 0,
        "shots_off": 0,
        "corners": 0,
        "possession": 0
    }

    for s in stats:
        code = s.get("type", {}).get("code")
        value = s.get("value", 0)

        if code == "shots_on_target":
            data["shots_on"] += value
        elif code == "shots_off_target":
            data["shots_off"] += value
        elif code == "corners":
            data["corners"] += value
        elif code == "ball_possession":
            data["possession"] += value

    return data

# ================== MAIN ==================
async def send_live_stats():
    matches = get_live_matches()

    if not matches:
        await bot.send_message(chat_id=CHAT_ID, text="❌ لا توجد مباريات مباشرة حاليًا في الدوري التركي.")
        return

    for match in matches:
        teams = match.get("participants", [])
        stats = match.get("statistics", [])

        if len(teams) < 2:
            continue

        home = teams[0]["name"]
        away = teams[1]["name"]

        s = parse_statistics(stats)

        message = (
            f"⚽ مباراة مباشرة (الدوري التركي – الدرجة الأولى)\n\n"
            f"{home} 🆚 {away}\n\n"
            f"🎯 تسديدات على المرمى: {s['shots_on']}\n"
            f"❌ تسديدات خارج: {s['shots_off']}\n"
            f"🚩 ركنيات: {s['corners']}\n"
            f"📊 استحواذ: {s['possession']}%\n"
        )

        await bot.send_message(chat_id=CHAT_ID, text=message)

async def main():
    await bot.send_message(chat_id=CHAT_ID, text="🤖 اختبار الدوري التركي الدرجة الأولى")
    await send_live_stats()

if __name__ == "__main__":
    asyncio.run(main())
