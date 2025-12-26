import os
import requests
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

# ================== ENV VARIABLES ==================
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
SPORTMONKS_API_KEY = os.getenv("SPORTMONKS_API_KEY")

LEAGUE_ID = 550  # 🇹🇷 الدوري التركي الدرجة الأولى

if not TELEGRAM_TOKEN:
    raise ValueError("❌ TELEGRAM_TOKEN غير موجود")

if not SPORTMONKS_API_KEY:
    raise ValueError("❌ SPORTMONKS_API_KEY غير موجود")

# ================== FUNCTIONS ==================
def get_matches():
    url = "https://api.sportmonks.com/v3/football/livescores"
    params = {
        "api_token": SPORTMONKS_API_KEY
    }

    r = requests.get(url, params=params)
    r.raise_for_status()
    data = r.json()

    matches = []
    for match in data.get("data", []):
        league = match.get("league", {})
        if league.get("id") == LEAGUE_ID:
            home = match["participants"][0]["name"]
            away = match["participants"][1]["name"]
            score = match["scores"][0]["score"] if match.get("scores") else "0 - 0"
            matches.append(f"{home} {score} {away}")

    return matches

# ================== TELEGRAM COMMAND ==================
async def live(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        matches = get_matches()

        if not matches:
            await update.message.reply_text(
                "🇹🇷 لا توجد مباريات مباشرة حاليًا في الدوري التركي الدرجة الأولى"
            )
        else:
            text = "🇹🇷 مباريات الدوري التركي الدرجة الأولى:\n\n"
            text += "\n".join(matches)
            await update.message.reply_text(text)

    except Exception as e:
        await update.message.reply_text(f"❌ خطأ:\n{e}")

# ================== MAIN ==================
def main():
    app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()
    app.add_handler(CommandHandler("live", live))
    app.run_polling()

if __name__ == "__main__":
    main()
