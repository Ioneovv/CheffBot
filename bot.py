import asyncio
import json
import requests
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, CallbackContext

# Загрузите JSON-файл с рецептами
RECIPE_URL = "https://drive.google.com/uc?export=download&id=1ZJRccW9YjpI0O8Q7eQ8PFCH5WC-6G-Yb"

def load_recipes():
    response = requests.get(RECIPE_URL)
    response.raise_for_status()  # Убедитесь, что запрос прошел успешно
    return response.json()

recipes = load_recipes()

def search_recipes(query):
    results = []
    for recipe in recipes:
        title = recipe.get('title', '').lower()
        ingredients = [ing['ingredient'].lower() for ing in recipe.get('ingredients', [])]
        if query.lower() in title or any(query.lower() in ing for ing in ingredients):
            results.append(recipe)
    return results

async def start(update: Update, context: CallbackContext):
    keyboard = [
        [InlineKeyboardButton("Поиск по названию", callback_data='search_by_title')],
        [InlineKeyboardButton("Поиск по ингредиентам", callback_data='search_by_ingredients')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text('Выберите способ поиска рецепта:', reply_markup=reply_markup)

async def button(update: Update, context: CallbackContext):
    query = update.callback_query
    await query.answer()
    
    if query.data == 'search_by_title':
        await query.edit_message_text(text="Введите название рецепта для поиска:")
        return 'search_by_title'
    elif query.data == 'search_by_ingredients':
        await query.edit_message_text(text="Введите ингредиент для поиска:")
        return 'search_by_ingredients'

async def handle_message(update: Update, context: CallbackContext):
    search_type = context.user_data.get('search_type')
    query = update.message.text
    if search_type:
        results = search_recipes(query)
        if results:
            response = "\n\n".join(f"Title: {recipe['title']}\nIngredients: {', '.join(ing['ingredient'] for ing in recipe['ingredients'])}" for recipe in results)
        else:
            response = "Ничего не найдено."
        
        await update.message.reply_text(response)
        context.user_data.pop('search_type', None)  # Очистите тип поиска

async def main():
    application = Application.builder().token("6953692387:AAEm-p8VtfqdmkHtbs8hxZWS-XNkdRN2lRE").build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CallbackQueryHandler(button))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    await application.initialize()
    await application.start()
    await application.updater.start_polling()
    await application.stop()

if __name__ == '__main__':
    try:
        loop = asyncio.get_running_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

    if loop.is_running():
        loop.create_task(main())
    else:
        asyncio.run(main())
