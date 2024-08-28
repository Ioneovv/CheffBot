import asyncio
import requests
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters, CallbackContext

# Загрузите JSON-файл с рецептами
RECIPE_URL = "https://drive.google.com/uc?export=download&id=1ZJRccW9YjpI0O8Q7eQ8PFCH5WC-6G-Yb"

def load_recipes():
    response = requests.get(RECIPE_URL)
    response.raise_for_status()
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
        context.user_data['search_type'] = 'search_by_title'
    elif query.data == 'search_by_ingredients':
        await query.edit_message_text(text="Введите ингредиент для поиска:")
        context.user_data['search_type'] = 'search_by_ingredients'

async def handle_message(update: Update, context: CallbackContext):
    user_input = update.message.text
    search_type = context.user_data.get('search_type')

    if search_type == 'search_by_title':
        results = search_recipes(user_input)
        if results:
            message = "Результаты поиска по названию:\n"
            for recipe in results:
                message += f"Название: {recipe['title']}\nИнгредиенты: {', '.join(ing['ingredient'] for ing in recipe['ingredients'])}\n\n"
        else:
            message = "Нет рецептов, соответствующих вашему запросу."
        await update.message.reply_text(message)
        context.user_data['search_type'] = None  # Сбросить тип поиска

    elif search_type == 'search_by_ingredients':
        results = search_recipes(user_input)
        if results:
            message = "Результаты поиска по ингредиентам:\n"
            for recipe in results:
                message += f"Название: {recipe['title']}\nИнгредиенты: {', '.join(ing['ingredient'] for ing in recipe['ingredients'])}\n\n"
        else:
            message = "Нет рецептов, соответствующих вашему запросу."
        await update.message.reply_text(message)
        context.user_data['search_type'] = None  # Сбросить тип поиска

async def main():
    # Создание экземпляра приложения и настройка токена
    application = Application.builder().token("6953692387:AAEm-p8VtfqdmkHtbs8hxZWS-XNkdRN2lRE").build()
    print("Bot application created.")

    # Обработчики команд и сообщений
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CallbackQueryHandler(button))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    print("Handlers added.")

    # Запуск бота
    await application.initialize()
    print("Bot initialized.")
    await application.start()
    print("Bot started.")
    await application.updater.start_polling()
    await application.stop()
    print("Bot stopped.")

if __name__ == '__main__':
    asyncio.run(main())
