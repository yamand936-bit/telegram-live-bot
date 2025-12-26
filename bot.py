import os
import requests
import asyncio
from telegram import Bot

# ================== ENV ==================
TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")
SPORTMONKS_API_KEY = os.getenv("SPORTMONKS_API_KEY")

if not TOKEN or not CHAT_ID or not SPORTMONKS_API_KEY:
    raise ValueError("❌ Missing environment variables")

bot = Bot(token=TOKEN)

# ================== CONSTANTS ==================
BASE_URL = "https://api.sportmonks.com/v3/football"
TURKEY_FIRST_DIVISION_ID = 550  # 🇹🇷 TFF 1. Lig

# ================== API ==================
def get_live_matches():
    """
    جلب المباريات المباشرة فقط
    بدون statistics لتفادي الأخطاء
    """
    url = f"{BASE_URL}/livescores"
    params = {
        "api_token": SPORTMONKS_API_KEY,
        "include": "participants",
        "filters": f"league_id:{TURKEY_FIRST_DIVISION_ID}"
    }

    r = requests.get(url, params=params, timeout=15)
    r.raise_for_status()
    return r.json().get("data", [])

# ================== MESSAGE ==================
def format_match(match):
    teams = match.get("participants", [])
    home = away = "؟"

    for t in teams:
        if t.get("meta", {}).get("location") == "home":
            home = t.get("name")
        elif t.get("meta", {}).get("location") == "away":
            away = t.get("name")

    return f"⚽ مباراة مباشرة\n{home} 🆚 {away}"

# ================== MAIN ==================
async def send_live_stats():
    try:
        matches = get_live_matches()

        if not matches:
            await bot.send_message(
                chat_id=CHAT_ID,
                text="🇹🇷 لا توجد مباريات مباشرة حاليًا في الدوري التركي – الدرجة الأولى"
            )
            return

        for match in matches:
            msg = format_match(match)
            await bot.send_message(chat_id=CHAT_ID, text=msg)

    except Exception as e:
        await bot.send_message(
            chat_id=CHAT_ID,
            text=f"❌ Error:\n{str(e)}"
        )

async def main():
    await bot.send_message(
        chat_id=CHAT_ID,
        text="🤖 اختبار الدوري التركي الدرجة الأولى – البوت يعمل"
    )
    await send_live_stats()

# ================== RUN ==================
if __name__ == "__main__":
    asyncio.run(main())
