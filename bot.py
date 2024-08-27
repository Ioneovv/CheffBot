import asyncio
from telegram import Update
from telegram.ext import Application, CommandHandler

async def start(update: Update, context):
    await update.message.reply_text("Привет! Я бот.")

async def main():
    application = Application.builder().token("6953692387:AAEm-p8VtfqdmkHtbs8hxZWS-XNkdRN2lRE").build()

    application.add_handler(CommandHandler("start", start))

    await application.run_polling()

if __name__ == '__main__':
    try:
        # Проверяем, запущен ли цикл событий
        loop = asyncio.get_running_loop()
    except RuntimeError:  # Нет запущенного цикла
        loop = None

    if loop and loop.is_running():
        # Если цикл событий уже запущен, используем его для запуска main()
        print("Event loop is running. Using current loop to run the bot.")
        loop.create_task(main())
    else:
        # Если цикл событий не запущен, запускаем его
        print("No running event loop. Using asyncio.run() to start the bot.")
        asyncio.run(main())
