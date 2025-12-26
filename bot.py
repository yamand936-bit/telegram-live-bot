import os
import asyncio
import requests
from telegram import Bot

# ================== ENV ==================
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")
SPORTMONKS_API_KEY = os.getenv("SPORTMONKS_API_KEY")

if not all([TELEGRAM_TOKEN, CHAT_ID, SPORTMONKS_API_KEY]):
    raise ValueError("❌ Missing environment variables")

bot = Bot(token=TELEGRAM_TOKEN)

# ================== CONSTANTS ==================
BASE_URL = "https://api.sportmonks.com/v3/football/livescores"

# ⚽ الدوري التركي الدرجة الأولى (TFF 1. Lig)
TURKEY_TFF1_LEAGUE_ID = 550

# ================== HELPERS ==================
def get_live_matches():
    params = {
        "api_token": SPORTMONKS_API_KEY,
        "include": "participants;statistics",
        "filters[league_id]": TURKEY_TFF1_LEAGUE_ID
    }

    r = requests.get(BASE_URL, params=params, timeout=30)
    r.raise_for_status()
    return r.json().get("data", [])

def parse_statistics(statistics):
    stats = {
        "shots_on_target": 0,
        "shots_off_target": 0,
        "corners": 0,
        "possession": 0
    }

    for s in statistics:
        type_info = s.get("type", {})
        code = type_info.get("code")

        value = s.get("value", 0)
        if isinstance(value, dict):
            value = value.get("total", 0)

        if code == "shots_on_target":
            stats["shots_on_target"] = value
        elif code == "shots_off_target":
            stats["shots_off_target"] = value
        elif code == "corners":
            stats["corners"] = value
        elif code == "ball_possession":
            stats["possession"] = value

    return stats

def format_match(match):
    teams = match.get("participants", [])
    home = teams[0]["name"] if len(teams) > 0 else "Home"
    away = teams[1]["name"] if len(teams) > 1 else "Away"

    stats = parse_statistics(match.get("statistics", []))

    message = (
        f"⚽ مباراة مباشرة\n"
        f"{home} 🆚 {away}\n\n"
        f"🎯 تسديدات على المرمى: {stats['shots_on_target']}\n"
        f"❌ تسديدات خارج: {stats['shots_off_target']}\n"
        f"🚩 ركنيات: {stats['corners']}\n"
        f"📊 استحواذ: {stats['possession']}%\n"
    )
    return message

# ================== MAIN LOOP ==================
async def send_live_stats():
    try:
        matches = get_live_matches()

        if not matches:
            await bot.send_message(
                chat_id=CHAT_ID,
                text="🤖 لا توجد مباريات مباشرة الآن (الدوري التركي الدرجة الأولى)"
            )
            return

        for match in matches:
            msg = format_match(match)
            await bot.send_message(chat_id=CHAT_ID, text=msg)

    except Exception as e:
        await bot.send_message(chat_id=CHAT_ID, text=f"❌ Error: {e}")

async def main():
    await bot.send_message(
        chat_id=CHAT_ID,
        text="🤖 اختبار الدوري التركي الدرجة الأولى – البوت يعمل"
    )

    while True:
        await send_live_stats()
        await asyncio.sleep(60)

if __name__ == "__main__":
    asyncio.run(main())
