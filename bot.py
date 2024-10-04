import asyncio
from telegram.ext import ApplicationBuilder

async def main():
    app = ApplicationBuilder().token("6953692387:AAEm-p8VtfqdmkHtbs8hxZWS-XNkdRN2lRE").build()
    await app.initialize()
    await app.start_polling()
    await app.idle()

if __name__ == '__main__':
    asyncio.run(main())
