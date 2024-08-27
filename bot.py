import asyncio
import json
import os
import random
from telegram import Update
from telegram.ext import Application, CommandHandler, CallbackContext

TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')

# Чтение рецептов из файла
def load_recipes():
    try:
        with open('recipes.json', 'r') as f:
            recipes = json.load(f)
        return recipes
    except (json.JSONDecodeError, FileNotFoundError) as e:
        print(f"Ошибка при чтении JSON файла: {e}")
        return []

recipes = load_recipes()

async def send_recipe(update: Update, context: CallbackContext):
    if recipes:
        recipe = random.choice(recipes)
        message = f"Название: {recipe.get('title', 'Неизвестно')}\nИнгредиенты: {recipe.get('ingredients', 'Неизвестно')}\nИнструкция: {recipe.get('instructions', 'Неизвестно')}"
        await update.message.reply_text(message)
    else:
        await update.message.reply_text("Рецепты не загружены или файл пуст.")

async def main():
    application = Application.builder().token(TELEGRAM_BOT_TOKEN).build()

    application.add_handler(CommandHandler("recipe", send_recipe))

    # Запуск бота
    await application.run_polling()

if __name__ == '__main__':
    try:
        asyncio.run(main())
    except RuntimeError as e:
        print(f"Ошибка при запуске бота: {e}")
