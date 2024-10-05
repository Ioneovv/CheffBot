import nest_asyncio
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

# Применяем nest_asyncio
nest_asyncio.apply()

# Определяем команды бота
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text('Привет! Я ваш кулинарный бот.')

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text('Как я могу помочь?')

async def main() -> None:
    # Создаем приложение бота
    application = ApplicationBuilder().token('6953692387:AAEm-p8VtfqdmkHtbs8hxZWS-XNkdRN2lRE').build()

    # Добавляем обработчики команд
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))

    # Запускаем бота
    await application.run_polling()

if __name__ == '__main__':
    import asyncio
    asyncio.run(main())
