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
        if not recipes:
            print("Файл рецептов пуст.")
        return recipes
    except json.JSONDecodeError as e:
        print(f"Ошибка при чтении JSON файла: {e}")
        return []
    except FileNotFoundError as e:
        print(f"Файл не найден: {e}")
        return []
    except Exception as e:
        print(f"Произошла ошибка: {e}")
        return []

recipes = load_recipes()

# Обработчик команды /recipe
async def send_recipe(update: Update, context: CallbackContext):
    if recipes:
        recipe = random.choice(recipes)
        message = (
            f"Название: {recipe.get('title', 'Неизвестно')}\n"
            f"Ингредиенты: {recipe.get('ingredients', 'Неизвестно')}\n"
            f"Инструкция: {recipe.get('instructions', 'Неизвестно')}"
        )
        await update.message.reply_text(message)
    else:
        await update.message.reply_text("Рецепты не загружены или файл пуст.")

# Основная функция
async def main():
    if not TELEGRAM_BOT_TOKEN:
        raise ValueError("Отсутствует токен бота. Убедитесь, что TELEGRAM_BOT_TOKEN установлен в переменных окружения.")
    
    application = Application.builder().token(TELEGRAM_BOT_TOKEN).build()
    application.add_handler(CommandHandler("recipe", send_recipe))

    # Запуск бота
    try:
        await application.run_polling()
    except Exception as e:
        print(f"Произошла ошибка при запуске бота: {e}")

if __name__ == '__main__':
    try:
        asyncio.get_event_loop().run_until_complete(main())
    except RuntimeError as e:
        if str(e) == 'This event loop is already running':
            print("Цикл событий уже запущен.")
        else:
            raise e
