from telegram import Bot
from telegram.ext import Updater, CommandHandler
import json
import os

# Получите токен из переменных окружения
TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
bot = Bot(token=TELEGRAM_BOT_TOKEN)

# Функция для отправки рецепта
def send_recipe(update, context):
    # Чтение рецептов из файла
    try:
        with open('recipes.json', 'r') as f:
            recipes = json.load(f)
        # Предположим, что recipes - это список рецептов
        # Выберите случайный рецепт
        import random
        recipe = random.choice(recipes)
        message = f"Название: {recipe['title']}\nИнгредиенты: {recipe['ingredients']}\nИнструкция: {recipe['instructions']}"
        bot.send_message(chat_id=update.effective_chat.id, text=message)
    except Exception as e:
        bot.send_message(chat_id=update.effective_chat.id, text=f"Ошибка: {e}")

def main():
    updater = Updater(token=TELEGRAM_BOT_TOKEN, use_context=True)
    dispatcher = updater.dispatcher

    # Обработчик команд
    dispatcher.add_handler(CommandHandler('recipe', send_recipe))

    # Запуск бота
    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()
