from telegram import Update
from telegram.ext import Application, CommandHandler

# Убираем async
def start(update: Update, context):
    update.message.reply_text("Привет! Я бот.")

def main():
    application = Application.builder().token("6953692387:AAEm-p8VtfqdmkHtbs8hxZWS-XNkdRN2lRE").build()

    # Убираем async
    application.add_handler(CommandHandler("start", start))

    # Убираем await и запускаем обычным способом
    application.run_polling()

if __name__ == '__main__':
    main()
