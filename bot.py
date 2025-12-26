import os
import requests
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
SPORTMONKS_API_KEY = os.getenv("SPORTMONKS_API_KEY")

LEAGUE_ID = 550  # الدوري التركي الدرجة الأولى

if not TELEGRAM_TOKEN:
    raise ValueError("❌ TELEGRAM_TOKEN غير موجود")

if not SPORTMONKS_API_KEY:
    raise ValueError("❌ SPORTMONKS_API_KEY غير موجود")


async def live(update: Update, context: ContextTypes.DEFAULT_TYPE):
    url = "https://api.sportmonks.com/v3/football/livescores"
    params = {
        "api_token": SPORTMONKS_API_KEY,
        "filters": f"league_id:{LEAGUE_ID}"
    }

    try:
        r = requests.get(url, params=params, timeout=15)
        r.raise_for_status()
        data = r.json().get("data", [])

        if not data:
            await update.message.reply_text(
                "🇹🇷 لا توجد مباريات مباشرة حاليًا في الدوري التركي الدرجة الأولى"
            )
            return

        msg = "🇹🇷 مباريات الدوري التركي الدرجة الأولى:\n\n"

        for match in data:
            home = match["participants"][0]["name"]
            away = match["participants"][1]["name"]
            score = match["scores"][0]["score"] if match.get("scores") else "0 - 0"
            minute = match["time"]["minute"] if match.get("time") else "?"

            msg += f"⚽ {home} {score} {away} ({minute}')\n"

        await update.message.reply_text(msg)

    except Exception as e:
        await update.message.reply_text(f"❌ خطأ: {e}")


def main():
    app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()
    app.add_handler(CommandHandler("live", live))
    app.run_polling()


if __name__ == "__main__":
    main()
