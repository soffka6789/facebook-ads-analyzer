import os
import logging
from datetime import datetime
import pytz
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes
from apscheduler.schedulers.background import BackgroundScheduler

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN", "8686753284:AAGOAIBCoWSmno-z6T635MHCyWWceZ3z_m4")
USER_ID = int(os.getenv("USER_ID", "5989342315"))
UKRAINE_TZ = pytz.timezone('Europe/Kyiv')

PRODUCTS = [
    {"name": "Портативна лампа", "price": "299-599", "ads": 287, "competitors": 34, "growth": 18, "rec": "ЗАПУСКАТИ ОДРАЗУ"},
    {"name": "Еко-пляшка", "price": "199-449", "ads": 412, "competitors": 12, "growth": 45, "rec": "ЗАПУСКАТИ МАКСИМАЛЬНО"},
    {"name": "Smart-кільце", "price": "499-899", "ads": 156, "competitors": 18, "growth": 28, "rec": "ГАРНИЙ ВИБІР"},
]

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("📊 Отримати звіт", callback_data='report')],
        [InlineKeyboardButton("🔥 Тренди", callback_data='trends')],
    ]
    await update.message.reply_text("Привіт! Я - Facebook Ads Bot", reply_markup=InlineKeyboardMarkup(keyboard))

async def report(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    msg = "TOP-10 ТОВАРІВ:\n\n"
    for i, p in enumerate(PRODUCTS, 1):
        msg += f"{i}. {p['name']} - {p['growth']:+d}% - {p['rec']}\n"
    await query.edit_message_text(msg)

async def trends(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    msg = "ТРЕНДОВІ ТОВАРИ:\n\n"
    for p in sorted(PRODUCTS, key=lambda x: x['growth'], reverse=True):
        msg += f"• {p['name']} - {p['growth']:+d}%\n"
    await query.edit_message_text(msg)

def main():
    app = Application.builder().token(TELEGRAM_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(report, pattern='report'))
    app.add_handler(CallbackQueryHandler(trends, pattern='trends'))
    
    scheduler = BackgroundScheduler(timezone=UKRAINE_TZ)
    scheduler.start()
    
    print("✅ БОТ ЗАПУЩЕН!")
    app.run_polling()

if __name__ == '__main__':
    main()
