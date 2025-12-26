import os
import asyncio
import requests
from telegram import Bot

# ================== ENV ==================
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
SPORTMONKS_API_KEY = os.getenv("SPORTMONKS_API_KEY")
CHAT_ID = os.getenv("CHAT_ID")

if not TELEGRAM_TOKEN or not SPORTMONKS_API_KEY or not CHAT_ID:
    raise ValueError("❌ Missing environment variables")

bot = Bot(token=TELEGRAM_TOKEN)

BASE_URL = "https://api.sportmonks.com/v3/football"

# ================== API ==================
def get_live_matches():
    url = f"{BASE_URL}/livescores"
    params = {
        "api_token": SPORTMONKS_API_KEY,
        "include": "participants;statistics"
    }
    r = requests.get(url, params=params, timeout=20)
    r.raise_for_status()
    return r.json().get("data", [])

# ================== STATS PARSER ==================
def parse_stats(statistics):
    stats = {
        "shots_on_target": 0,
        "shots_off_target": 0,
        "corners": 0,
        "possession": 0
    }

    for s in statistics:
        stat_type = s.get("type")
        data = s.get("data")

        if not stat_type or not data:
            continue

        code = stat_type.get("code")
        value = data.get("value", 0)

        if code == "shots_on_target":
            stats["shots_on_target"] += value
        elif code == "shots_off_target":
            stats["shots_off_target"] += value
        elif code == "corners":
            stats["corners"] += value
        elif code == "ball_possession":
            stats["possession"] = value

    return stats

# ================== MESSAGE ==================
def build_message(match):
    teams = match.get("participants", [])
    home = away = "Unknown"

    for t in teams:
        if t.get("meta", {}).get("location") == "home":
            home = t.get("name")
        elif t.get("meta", {}).get("location") == "away":
            away = t.get("name")

    stats = parse_stats(match.get("statistics", []))

    return (
        f"⚽ مباراة مباشرة\n"
        f"{home} 🆚 {away}\n\n"
        f"🎯 تسديدات على المرمى: {stats['shots_on_target']}\n"
        f"❌ تسديدات خارج: {stats['shots_off_target']}\n"
        f"🚩 ركنيات: {stats['corners']}\n"
        f"📊 استحواذ: {stats['possession']}%"
    )

# ================== MAIN ==================
async def send_live_stats():
    matches = get_live_matches()

    if not matches:
        await bot.send_message(chat_id=CHAT_ID, text="❌ لا توجد مباريات مباشرة الآن")
        return

    for match in matches:
        try:
            message = build_message(match)
            await bot.send_message(chat_id=CHAT_ID, text=message)
        except Exception as e:
            await bot.send_message(chat_id=CHAT_ID, text=f"⚠️ خطأ: {e}")

async def main():
    await bot.send_message(chat_id=CHAT_ID, text="🤖 البوت شغّال باستخدام SportMonks (إحصائيات حقيقية)")
    await send_live_stats()

if __name__ == "__main__":
    asyncio.run(main())
