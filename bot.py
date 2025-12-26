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

# ================== API ==================
BASE_URL = "https://api.sportmonks.com/v3/football/livescores"


def get_live_matches():
    url = f"{BASE_URL}?api_token={SPORTMONKS_API_KEY}&include=participants;statistics"
    r = requests.get(url, timeout=20)
    r.raise_for_status()
    return r.json().get("data", [])


def parse_statistics(stats):
    result = {
        "shots_on": 0,
        "shots_off": 0,
        "corners": 0,
        "possession": 0
    }

    for s in stats:
        stat_type = s.get("type", {}).get("name", "").lower()
        value = s.get("value", 0)

        if "shots on target" in stat_type:
            result["shots_on"] += value
        elif "shots off target" in stat_type:
            result["shots_off"] += value
        elif "corners" in stat_type:
            result["corners"] += value
        elif "ball possession" in stat_type:
            result["possession"] = value

    return result


async def send_live_stats():
    matches = get_live_matches()

    if not matches:
        await bot.send_message(chat_id=CHAT_ID, text="⚠️ لا توجد مباريات مباشرة الآن")
        return

    for match in matches:
        teams = match.get("participants", [])
        if len(teams) < 2:
            continue

        home = teams[0]["name"]
        away = teams[1]["name"]

        stats = parse_statistics(match.get("statistics", []))

        message = (
            f"⚽ مباراة مباشرة\n"
            f"{home} 🆚 {away}\n\n"
            f"🎯 تسديدات على المرمى: {stats['shots_on']}\n"
            f"❌ تسديدات خارج: {stats['shots_off']}\n"
            f"🚩 ركنيات: {stats['corners']}\n"
            f"📊 استحواذ: {stats['possession']}%"
        )

        await bot.send_message(chat_id=CHAT_ID, text=message)


# ================== RUN ==================
async def main():
    await bot.send_message(
        chat_id=CHAT_ID,
        text="🤖 البوت يعمل الآن مع إحصائيات SportMonks"
    )

    while True:
        try:
            await send_live_stats()
        except Exception as e:
            await bot.send_message(chat_id=CHAT_ID, text=f"❌ Error: {e}")
        await asyncio.sleep(60)


if __name__ == "__main__":
    asyncio.run(main())
