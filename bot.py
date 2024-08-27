from telegram.ext import Application, CommandHandler

async def start(update, context):
    await update.message.reply_text("Привет!")

async def main():
    application = Application.builder().token('YOUR_BOT_TOKEN').build()
    application.add_handler(CommandHandler('start', start))
    await application.run_polling()

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
