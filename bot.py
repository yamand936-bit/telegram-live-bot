import os
import requests
import asyncio
from telegram import Bot

# ====== ENV ======
SPORTMONKS_API_KEY = os.getenv("SPORTMONKS_API_KEY")
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

if not SPORTMONKS_API_KEY or not TELEGRAM_TOKEN or not CHAT_ID:
    raise ValueError("❌ Missing environment variables")

bot = Bot(token=TELEGRAM_TOKEN)

BASE_URL = "https://api.sportmonks.com/v3/football/livescores"

LEAGUE_ID = 550  # 🇹🇷 Turkey 1. Lig


# ====== GET LIVE MATCHES ======
def get_live_matches():
    params = {
        "api_token": SPORTMONKS_API_KEY,
        "include": "participants",
    }

    response = requests.get(BASE_URL, params=params, timeout=15)

    if response.status_code != 200:
        print(response.text)
        return []

    data = response.json().get("data", [])

    matches = []
    for match in data:
        if match.get("league_id") == LEAGUE_ID:
            matches.append(match)

    return matches


# ====== SEND MESSAGE ======
async def send_live_matches():
    matches = get_live_matches()

    if not matches:
        await bot.send_message(
            chat_id=CHAT_ID,
            text="🇹🇷 لا توجد مباريات مباشرة حاليًا في الدوري التركي الدرجة الأولى"
        )
        return

    for match in matches:
        home = away = "?"
        for team in match.get("participants", []):
            if team.get("meta", {}).get("location") == "home":
                home = team.get("name", "?")
            elif team.get("meta", {}).get("location") == "away":
                away = team.get("name", "?")

        message = (
            "⚽ مباراة مباشرة\n\n"
            f"{home} 🆚 {away}\n"
            f"⏱ الدقيقة: {match.get('minute', '؟')}"
        )

        await bot.send_message(chat_id=CHAT_ID, text=message)


# ====== MAIN ======
async def main():
    await send_live_matches()


if __name__ == "__main__":
    asyncio.run(main())
