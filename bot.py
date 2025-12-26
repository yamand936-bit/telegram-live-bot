import os
import asyncio
import requests
from telegram import Bot

# ================== ENV ==================
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")
SPORTMONKS_API_KEY = os.getenv("SPORTMONKS_API_KEY")

if not TELEGRAM_TOKEN or not CHAT_ID or not SPORTMONKS_API_KEY:
    raise ValueError("❌ Missing environment variables")

bot = Bot(token=TELEGRAM_TOKEN)

BASE_URL = "https://api.sportmonks.com/v3/football"

# ================== FETCH LIVE MATCHES ==================
def get_live_matches():
    url = f"{BASE_URL}/livescores"
    params = {
        "api_token": SPORTMONKS_API_KEY,
        "include": "participants;statistics"
    }
    r = requests.get(url, params=params, timeout=15)
    r.raise_for_status()
    return r.json().get("data", [])

# ================== PARSE STATISTICS ==================
def parse_stats(statistics):
    result = {
        "shots_on_target": 0,
        "shots_off_target": 0,
        "corners": 0,
        "possession": 0
    }

    for s in statistics:
        # بعض العناصر لا تحتوي type
        stat_type = s.get("type")
        if not stat_type:
            continue

        code = stat_type.get("code")
        value = s.get("value", 0)

        if code == "shots_on_target":
            result["shots_on_target"] += int(value)
        elif code == "shots_off_target":
            result["shots_off_target"] += int(value)
        elif code == "corners":
            result["corners"] += int(value)
        elif code == "possession":
            # نأخذ المتوسط
            try:
                result["possession"] = int(float(value))
            except:
                pass

    return result

# ================== SEND LIVE STATS ==================
async def send_live_stats():
    matches = get_live_matches()

    if not matches:
        await bot.send_message(chat_id=CHAT_ID, text="⚠️ لا توجد مباريات مباشرة الآن")
        return

    for match in matches:
        participants = match.get("participants", [])
        statistics = match.get("statistics", [])

        if len(participants) < 2:
            continue

        home = participants[0]["name"]
        away = participants[1]["name"]

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
        await asyncio.sleep(1)

# ================== MAIN LOOP ==================
async def main():
    await bot.send_message(chat_id=CHAT_ID, text="🤖 البوت شغّال باستخدام SportMonks (إحصائيات)")
    while True:
        try:
            await send_live_stats()
        except Exception as e:
            await bot.send_message(chat_id=CHAT_ID, text=f"❌ Error:\n{e}")
        await asyncio.sleep(60)

if __name__ == "__main__":
    asyncio.run(main())
