from telegram import Update
from telegram.ext import Application, CommandHandler, CallbackContext
import json
import os
import random
import asyncio

# Получите токен из переменных окружения
TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')

# Чтение рецептов из файла
def load_recipes():
    try:
        with open('recipes.json', 'r') as f:
            recipes = json.load(f)
        return recipes
    except json.JSONDecodeError as e:
        print(f"Ошибка при чтении JSON файла: {e}")
        return []
    except FileNotFoundError as e:
        print(f"Файл не найден: {e}")
        return []

recipes = load_recipes()

# Обработчик команды /recipe
async def send_recipe(update: Update, context: CallbackContext):
    if recipes:
        recipe = random.choice(recipes)
        message = f"Название: {recipe.get('title', 'Неизвестно')}\nИнгредиенты: {recipe.get('ingredients', 'Неизвестно')}\nИнструкция: {recipe.get('instructions', 'Неизвестно')}"
        await update.message.reply_text(message)
    else:
        await update.message.reply_text("Рецепты не загружены или файл пуст.")

# Основная функция
async def main():
    application = Application.builder().token(TELEGRAM_BOT_TOKEN).build()

    application.add_handler(CommandHandler("recipe", send_recipe))

    # Запуск бота
    await application.run_polling()

if __name__ == '__main__':
    # Получаем текущий цикл событий
    loop = asyncio.get_event_loop()
    # Запускаем основной код, если цикл событий еще не запущен
    if not loop.is_running():
        loop.run_until_complete(main())
    else:
        # Если цикл событий уже запущен, запускаем основную функцию с помощью asyncio.create_task
        asyncio.create_task(main())
