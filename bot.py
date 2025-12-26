import os
import requests
from telegram import Bot

# ===== ENV =====
TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")
SPORTMONKS_API_KEY = os.getenv("SPORTMONKS_API_KEY")

bot = Bot(token=TOKEN)

# ===== CONSTANTS =====
LEAGUE_ID = 550  # 🇹🇷 TFF 1. Lig
API_URL = "https://api.sportmonks.com/v3/football/livescores"


def get_live_scores():
    params = {
        "api_token": SPORTMONKS_API_KEY
    }

    response = requests.get(API_URL, params=params, timeout=20)
    response.raise_for_status()
    data = response.json().get("data", [])

    matches = []

    for match in data:
        league = match.get("league", {})
        if league.get("id") != LEAGUE_ID:
            continue

        participants = match.get("participants", [])
        if len(participants) < 2:
            continue

        home = participants[0]
        away = participants[1]

        score = match.get("scores", {})
        home_goals = score.get("home", 0)
        away_goals = score.get("away", 0)

        matches.append(
            f"⚽ {home['name']} {home_goals} - {away_goals} {away['name']}"
        )

    return matches


def main():
    try:
        matches = get_live_scores()

        if not matches:
            message = "🇹🇷 لا توجد مباريات مباشرة حاليًا في الدوري التركي الدرجة الأولى"
        else:
            message = "🇹🇷 مباريات مباشرة – الدوري التركي الدرجة الأولى:\n\n"
            message += "\n".join(matches)

        bot.send_message(chat_id=CHAT_ID, text=message)

    except Exception as e:
        bot.send_message(
            chat_id=CHAT_ID,
            text=f"❌ خطأ:\n{str(e)}"
        )


if __name__ == "__main__":
    main()
