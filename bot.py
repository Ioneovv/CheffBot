import asyncio
from telegram.ext import Application, CommandHandler

async def start(update, context):
    await update.message.reply_text("Привет, мир!")

async def main():
    # Создание экземпляра приложения с токеном вашего бота
    application = Application.builder().token('6953692387:AAEm-p8VtfqdmkHtbs8hxZWS-XNkdRN2lRE').build()
    
    # Добавление обработчика команды /start
    application.add_handler(CommandHandler('start', start))
    
    # Запуск бота
    await application.run_polling()

if __name__ == '__main__':
    # Получение текущего цикла событий
    loop = asyncio.get_event_loop()
    try:
        # Запуск основного метода
        loop.run_until_complete(main())
    finally:
        # Закрытие цикла событий, если он был закрыт
        if loop.is_running():
            loop.stop()
        loop.close()
