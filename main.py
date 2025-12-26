import os
import asyncio
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, ContextTypes

BOT_TOKEN = os.environ["TELEGRAM_BOT_TOKEN"]

LEAGUES = {
    "🏴 Premier League": 8,
    "🇪🇸 La Liga": 564,
    "🇮🇹 Serie A": 384,
    "🇩🇪 Bundesliga": 82,
}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton(name, callback_data=str(lid))]
        for name, lid in LEAGUES.items()
    ]
    await update.message.reply_text(
        "⚽ اختر الدوري:",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

async def choose_league(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    await query.edit_message_text("✅ تم اختيار الدوري")

async def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(choose_league))
    print("Bot is running...")
    await app.run_polling()

if __name__ == "__main__":
    asyncio.run(main())
