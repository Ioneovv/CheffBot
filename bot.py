import logging
import json
import asyncio
import aiohttp
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CallbackContext, CommandHandler, CallbackQueryHandler

# Логирование
logging.basicConfig(level=logging.INFO)

# Функция для загрузки рецептов из репозитория
async def load_recipes():
    url = "https://github.com/Ioneovv/CheffBot/blob/main/recipes_part1.json"  # замените на вашу ссылку
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            if response.status == 200:
                return await response.json()
            else:
                logging.error(f"Ошибка загрузки рецептов: {response.status}")
                return []

recipes = asyncio.run(load_recipes())

# Эмодзи категорий
CATEGORY_EMOJIS = {
    "Салаты": "🥗", "Супы": "🍲", "Десерты": "🍰",
    "Основные блюда": "🍽", "Закуски": "🥪", "Напитки": "🥤"
}

# Пользовательские данные: избранное, история
user_data = {}

# Команда /start
async def start(update: Update, context: CallbackContext):
    user_id = update.effective_user.id
    user_data[user_id] = {'favorites': [], 'history': []}

    categories = set(recipe.get('category') for recipe in recipes)
    keyboard = [[InlineKeyboardButton(f"{CATEGORY_EMOJIS.get(cat, '🍴')} {cat}", callback_data=f'category_{cat}_0')] for cat in sorted(categories)]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text('Выберите категорию рецептов:', reply_markup=reply_markup)

# Остальные функции (show_favorites, search_recipes, add_to_favorites и т.д.) остаются без изменений...

# Главная функция
async def main():
    application = ApplicationBuilder().token("6953692387:AAEm-p8VtfqdmkHtbs8hxZWS-XNkdRN2lRE").build()

    application.add_handler(CommandHandler("start", start))
    # Остальные обработчики...
    
    await application.start()
    await application.updater.start_polling()
    await asyncio.Event().wait()

if __name__ == '__main__':
    asyncio.run(main())
