import os
import requests
import asyncio
from telegram import Bot

# ================== ENV ==================
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")
SPORTMONKS_API_KEY = os.getenv("SPORTMONKS_API_KEY")

if not TELEGRAM_TOKEN or not CHAT_ID or not SPORTMONKS_API_KEY:
    raise ValueError("❌ Missing environment variables")

bot = Bot(token=TELEGRAM_TOKEN)

BASE_URL = "https://api.sportmonks.com/v3/football"

# ================== HELPERS ==================
def get_live_matches():
    url = f"{BASE_URL}/livescores"
    params = {
        "api_token": SPORTMONKS_API_KEY,
        "filters[league_id]": 550,  # 🇹🇷 TFF 1. Lig
        "include": "participants;statistics"
    }

    r = requests.get(url, params=params, timeout=20)
    r.raise_for_status()
    return r.json().get("data", [])


def parse_stats(statistics):
    result = {
        "shots_on_target": 0,
        "shots_off_target": 0,
        "corners": 0,
        "possession": 0
    }

    for s in statistics:
        # حماية من الأخطاء
        stat_type = s.get("type")
        if not stat_type:
            continue

        code = stat_type.get("code")
        value = s.get("value", 0)

        if code == "shots_on_target":
            result["shots_on_target"] += value
        elif code == "shots_off_target":
            result["shots_off_target"] += value
        elif code == "corners":
            result["corners"] += value
        elif code == "possession":
            result["possession"] += value

    return result


async def send_live_stats():
    matches = get_live_matches()

    if not matches:
        await bot.send_message(chat_id=CHAT_ID, text="⚽ لا توجد مباريات مباشرة في الدوري التركي الدرجة الأولى")
        return

    for match in matches:
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
            f"📊 استحواذ: {parsed['possession']}%\n"
        )

        await bot.send_message(chat_id=CHAT_ID, text=message)


# ================== MAIN ==================
async def main():
    await bot.send_message(chat_id=CHAT_ID, text="🤖 البوت يعمل – تجربة الدوري التركي الدرجة الأولى")
    await send_live_stats()


if __name__ == "__main__":
    asyncio.run(main())
