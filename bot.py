import os
import asyncio
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN", "TOKEN")
USER_ID = int(os.getenv("USER_ID", "5989342315"))

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Привіт! Я живий! 🤖")

async def report(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = "TOP-10 ТОВАРІВ:\n1. Портативна лампа +18%\n2. Еко-пляшка +45%"
    await update.message.reply_text(msg)

async def main():
    app = Application.builder().token(TELEGRAM_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("report", report))

    print("✅ БОТ ЗАПУЩЕН!")
    await app.run_polling()

if __name__ == '__main__':
    asyncio.run(main())
