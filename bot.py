from telegram import Update
from telegram.ext import Application, CommandHandler

async def start(update: Update, context):
    await update.message.reply_text("Привет! Я бот.")

async def main():
    application = Application.builder().token("6953692387:AAEm-p8VtfqdmkHtbs8hxZWS-XNkdRN2lRE").build()

    application.add_handler(CommandHandler("start", start))

    await application.run_polling()

if __name__ == '__main__':
    import asyncio
    asyncio.run(main())
