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
    
    if query.data.startswith('recipe_'):
        # Обработка нажатия кнопки рецепта
        recipe_index = int(query.data.split('_')[1])
        recipe = recipes[recipe_index]
        recipe_text = f"**{recipe['title']}**\n\n"
        recipe_text += f"Ингредиенты:\n"
        for ingredient in recipe.get('ingredients', []):
            recipe_text += f"- {ingredient['ingredient']} ({ingredient.get('quantity', '')})\n"
        recipe_text += f"\nПриготовление:\n{recipe.get('instructions', '')}"
        await query.message.reply_text(recipe_text, parse_mode='Markdown')
        return

    if query.data == 'search_by_title':
        await query.edit_message_text(text="Введите название рецепта для поиска:")
        context.user_data['search_type'] = 'search_by_title'
    elif query.data == 'search_by_ingredients':
        await query.edit_message_text(text="Введите ингредиент для поиска:")
        context.user_data['search_type'] = 'search_by_ingredients'

async def handle_message(update: Update, context: CallbackContext):
    query = update.message.text
    search_type = context.user_data.get('search_type')

    if search_type == 'search_by_title':
        results = search_recipes(query)
        if not results:
            await update.message.reply_text("Ничего не найдено.")
            return

        keyboard = []
        for i, recipe in enumerate(results):
            keyboard.append([InlineKeyboardButton(recipe['title'], callback_data=f'recipe_{i}')])
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.message.reply_text("Выберите рецепт:", reply_markup=reply_markup)
    
    elif search_type == 'search_by_ingredients':
        results = search_recipes(query)
        if not results:
            await update.message.reply_text("Ничего не найдено.")
            return

        keyboard = []
        for i, recipe in enumerate(results):
            keyboard.append([InlineKeyboardButton(recipe['title'], callback_data=f'recipe_{i}')])
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.message.reply_text("Выберите рецепт:", reply_markup=reply_markup)
    
    else:
        await update.message.reply_text("Пожалуйста, выберите способ поиска.")

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
    print("Bot is polling.")
    await asyncio.Event().wait()  # Ожидание бесконечно
    print("Bot stopped.")

if __name__ == '__main__':
    asyncio.run(main())
