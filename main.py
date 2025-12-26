import os
import time
import requests
from telegram import (
    Bot,
    Update,
    InlineKeyboardButton,
    InlineKeyboardMarkup
)
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    CallbackQueryHandler,
    ContextTypes
)

BOT_TOKEN = os.environ["TELEGRAM_BOT_TOKEN"]
SPORTMONKS_API_KEY = os.environ["SPORTMONKS_API_KEY"]

LEAGUES = {
    "🏴 Premier League": 8,
    "🇪🇸 La Liga": 564,
    "🇮🇹 Serie A": 384,
    "🇩🇪 Bundesliga": 82,
    "🇫🇷 Ligue 1": 301
}

user_league = {}
sent_goals = set()

# ---------- START ----------
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton(name, callback_data=str(lid))]
        for name, lid in LEAGUES.items()
    ]
    await update.message.reply_text(
        "⚽ اختر الدوري:",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

# ---------- LEAGUE SELECT ----------
async def select_league(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    league_id = int(query.data)
    user_league[query.from_user.id] = league_id

    await query.edit_message_text(
        "✅ تم اختيار الدوري\n📡 سيتم إرسال المباريات المباشرة"
    )

# ---------- SPORTMONKS ----------
def get_live_matches(league_id):
    url = "https://api.sportmonks.com/v3/football/fixtures/live"
    params = {
        "api_token": SPORTMONKS_API_KEY,
        "include": "participants,scores",
        "filters": f"league_id:{league_id}"
    }
    r = requests.get(url, params=params, timeout=20)
    return r.json().get("data", [])

# ---------- LOOP ----------
async def live_loop(app):
    while True:
        for user_id, league_id in user_league.items():
            matches = get_live_matches(league_id)

            for match in matches:
                if len(match["participants"]) < 2:
                    continue

                home, away = match["participants"]
                hs = as_ = 0

                for s in match.get("scores", []):
                    if s["description"] == "CURRENT":
                        if s["participant_id"] == home["id"]:
                            hs = s["score"]["goals"]
                        elif s["participant_id"] == away["id"]:
                            as_ = s["score"]["goals"]

                key = f"{user_id}-{match['id']}-{hs}-{as_}"
                if key not in sent_goals:
                    sent_goals.add(key)
                    await app.bot.send_message(
                        chat_id=user_id,
                        text=f"⚽ {home['name']} {hs} - {as_} {away['name']}"
                    )
        time.sleep(60)

# ---------- MAIN ----------
if __name__ == "__main__":
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(select_league))

    app.create_task(live_loop(app))
    app.run_polling()
