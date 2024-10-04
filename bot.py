from telegram.ext import ApplicationBuilder

async def main():
    app = ApplicationBuilder().token("6953692387:AAEm-p8VtfqdmkHtbs8hxZWS-XNkdRN2lRE").build()
    await app.initialize()
    await app.run_polling()  # Запуск polling
    await app.idle()

if __name__ == '__main__':
    main()  # просто вызовите main без asyncio.run()
