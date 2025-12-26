import os
import requests
import asyncio
from telegram import Bot

# ================== ENV ==================
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")
SPORTMONKS_API_KEY = os.getenv("SPORTMONKS_API_KEY")

if not all([TELEGRAM_TOKEN, CHAT_ID, SPORTMONKS_API_KEY]):
    raise ValueError("❌ Missing ENV variables")

bot = Bot(token=TELEGRAM_TOKEN)

BASE_URL = "https://api.sportmonks.com/v3/football"

# الدوري التركي الدرجة الأولى
TURKEY_TFF1_LEAGUE_ID = 550


# ================== API ==================
def get_live_matches():
    url = f"{BASE_URL}/livescores"
    params = {
        "api_token": SPORTMONKS_API_KEY,
        "include": "participants",
    }

    r = requests.get(url, params=params, timeout=20)
    r.raise_for_status()

    matches = r.json().get("data", [])
    return [
        m for m in matches
        if m.get("league", {}).get("id") == TURKEY_TFF1_LEAGUE_ID
    ]


def get_match_statistics(fixture_id):
    url = f"{BASE_URL}/fixtures/{fixture_id}"
    params = {
        "api_token": SPORTMONKS_API_KEY,
        "include": "statistics"
    }

    r = requests.get(url, params=params, timeout=20)
    r.raise_for_status()

    return r.json().get("data", {}).get("statistics", [])


# ================== PARSER ==================
def parse_stats(statistics):
    stats = {
        "shots_on_target": 0,
        "shots_off_target": 0,
        "corners": 0,
        "possession": 0,
    }

    for s in statistics:
        type_info = s.get("type")
        if not type_info:
            continue

        name = type_info.get("name", "").lower()
        value = s.get("value", 0)

        if "shots on target" in name:
            stats["shots_on_target"] += int(value or 0)

        elif "shots off target" in name:
            stats["shots_off_target"] += int(value or 0)

        elif "corner" in name:
            stats["corners"] += int(value or 0)

        elif "possession" in name:
            stats["possession"] = int(value or 0)

    return stats


# ================== TELEGRAM ==================
async def send_live_stats():
    matches = get_live_matches()

    if not matches:
        await bot.send_message(
            chat_id=CHAT_ID,
            text="🇹🇷 لا توجد مباريات مباشرة حاليًا في الدوري التركي الدرجة الأولى"
        )
        return

    for match in matches:
        home = match["participants"][0]["name"]
        away = match["participants"][1]["name"]

        statistics = get_match_statistics(match["id"])
        stats = parse_stats(statistics)

        message = (
            f"⚽ مباراة مباشرة – الدوري التركي الدرجة الأولى\n\n"
            f"{home} 🆚 {away}\n\n"
            f"🎯 تسديدات على المرمى: {stats['shots_on_target']}\n"
            f"❌ تسديدات خارج: {stats['shots_off_target']}\n"
            f"🚩 ركنيات: {stats['corners']}\n"
            f"📊 استحواذ: {stats['possession']}%\n"
        )

        await bot.send_message(chat_id=CHAT_ID, text=message)


# ================== MAIN ==================
async def main():
    await bot.send_message(
        chat_id=CHAT_ID,
        text="🤖 اختبار الدوري التركي الدرجة الأولى – البوت يعمل"
    )
    await send_live_stats()


if __name__ == "__main__":
    asyncio.run(main())
