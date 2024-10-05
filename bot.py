import logging
import json
import asyncio
import aiohttp
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CallbackContext, CommandHandler, CallbackQueryHandler

# Логирование
logging.basicConfig(level=logging.INFO)

# Функция для загрузки рецептов из файла
async def load_recipes():
    url = "https://raw.githubusercontent.com/Ioneovv/CheffBot/main/recipes_part1.json"  # Убедитесь, что этот URL корректен
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            response.raise_for_status()  # Поднять исключение, если статус код не 200
            return await response.json()

recipes = asyncio.run(load_recipes())

# Ваши остальные функции остаются без изменений

# Основная логика (категории, рецепты)
async def category_button(update: Update, context: CallbackContext):
    query = update.callback_query
    category = query.data.split('_')[1]

    recipes_in_category = [recipe for recipe in recipes if recipe.get('category') == category]
    if recipes_in_category:
        keyboard = [[InlineKeyboardButton(f"🍽 {recipe['title']}", callback_data=f'recipe_{i}')] for i, recipe in enumerate(recipes_in_category)]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.message.edit_text("Выберите рецепт:", reply_markup=reply_markup)

# ... остальной код без изменений

# Главная функция
async def main():
    application = ApplicationBuilder().token("6953692387:AAEm-p8VtfqdmkHtbs8hxZWS-XNkdRN2lRE").build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("search", search_recipes))
    application.add_handler(CommandHandler("favorites", show_favorites))
    application.add_handler(CommandHandler("history", show_history))
    application.add_handler(CommandHandler("menu", menu))
    application.add_handler(CallbackQueryHandler(category_button, pattern='^category_'))
    application.add_handler(CallbackQueryHandler(show_recipe, pattern='^recipe_'))
    application.add_handler(CallbackQueryHandler(add_to_favorites, pattern='^favorite_'))
    application.add_handler(CallbackQueryHandler(rate_recipe, pattern='^rate_'))

    await application.start()
    await application.updater.start_polling()
    await asyncio.Event().wait()

if __name__ == '__main__':
    asyncio.run(main())
