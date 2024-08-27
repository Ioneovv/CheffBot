import json
import os
from telegram import Update
from telegram.ext import Application, CommandHandler, CallbackContext
import asyncio

TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')

# Загрузка рецептов из файла
def load_recipes():
    try:
        with open('recipes.json', 'r', encoding='utf-8') as f:
            recipes = json.load(f)
        return recipes
    except (json.JSONDecodeError, FileNotFoundError) as e:
        print(f"Ошибка загрузки рецептов: {e}")
        return []

recipes = load_recipes()

# Поиск рецептов по названию
def search_by_title(title):
    results = [recipe for recipe in recipes if title.lower() in recipe['title'].lower()]
    return results

# Поиск рецептов по ингредиентам
def search_by_ingredient(ingredient):
    results = [recipe for recipe in recipes if any(ingredient.lower() in ing['ingredient'].lower() for ing in recipe['ingredients'])]
    return results

# Команда /search для поиска по названию
async def search(update: Update, context: CallbackContext):
    query = ' '.join(context.args)
    if not query:
        await update.message.reply_text("Пожалуйста, укажите название рецепта или ингредиента для поиска.")
        return
    
    # Попробуйте сначала найти по названию
    results = search_by_title(query)
    
    # Если нет результатов, попробуйте найти по ингредиенту
    if not results:
        results = search_by_ingredient(query)
    
    if results:
        response = "\n\n".join([f"**{recipe['title']}**\n" + "\n".join([f"{ing['amount']} {ing['ingredient']}" for ing in recipe['ingredients']]) for recipe in results])
        await update.message.reply_text(response, parse_mode='Markdown')
    else:
        await update.message.reply_text("Не удалось найти рецепты по вашему запросу.")

# Функция для запуска бота
async def main():
    application = Application.builder().token(TELEGRAM_BOT_TOKEN).build()

    # Регистрация команды поиска
    application.add_handler(CommandHandler("search", search))

    # Запуск бота
    await application.run_polling()

# Запуск основной функции
if __name__ == "__main__":
    # Используем текущий цикл событий
    loop = asyncio.get_event_loop()
    try:
        loop.run_until_complete(main())
    except Exception as e:
        print(f"Ошибка: {e}")
    finally:
        loop.close()
