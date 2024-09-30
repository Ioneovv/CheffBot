import logging
import re
import aiohttp
import asyncio
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CallbackContext, CommandHandler, CallbackQueryHandler

# Логирование
logging.basicConfig(level=logging.INFO)

# Прямая ссылка для загрузки рецептов
RECIPE_URL = 'https://drive.google.com/uc?id=1xHKBF9dBVJBqeO-tT6CxCgAx34TG46em'

# Эмодзи для категорий
CATEGORY_EMOJIS = {
    "Салаты": "🥗",
    "Супы": "🍲",
    "Десерты": "🍰",
    "Тесто": "🥞",
    "Хлеб": "🍞",
    "Основные блюда": "🍽",
    "Закуски": "🥪",
    "Напитки": "🥤",
    "Вегетарианские": "🥦",
    "Диетические": "🥗",
    "Завтраки": "🍳",
    "Паста": "🍝"
}

# Ключевые слова для каждой категории
CATEGORIES = {
    # ... (как в вашем коде)
}

# Максимальное количество кнопок на странице
BUTTONS_PER_PAGE = 5

async def load_recipes():
    async with aiohttp.ClientSession() as session:
        try:
            async with session.get(RECIPE_URL) as response:
                response.raise_for_status()
                return await response.json()
        except Exception as e:
            logging.error(f"Ошибка загрузки рецептов: {e}")
            return []

def get_categories(recipes):
    categories = set(recipe.get('category') for recipe in recipes)
    return sorted(categories)

def format_recipe(recipe):
    # ... (как в вашем коде)

def categorize_recipe(recipe_title):
    # ... (как в вашем коде)

async def start(update: Update, context: CallbackContext):
    recipes = await load_recipes()  # Загружаем рецепты асинхронно
    if not recipes:
        await update.message.reply_text("Не удалось загрузить рецепты. Пожалуйста, попробуйте позже.")
        return

    categories = get_categories(recipes)
    keyboard = [[InlineKeyboardButton(f"{CATEGORY_EMOJIS.get(category, '🍴')} {category}", callback_data=f'category_{category}_0')] for category in categories]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text('Выберите категорию рецептов:', reply_markup=reply_markup)

async def category_button(update: Update, context: CallbackContext):
    query = update.callback_query
    await query.answer()
    data = query.data.split('_')
    category = data[1]
    page = int(data[2])
    recipes_in_category = [recipe for recipe in recipes if categorize_recipe(recipe['title']) == category]

    if not recipes_in_category:
        await query.message.reply_text("Нет рецептов в этой категории.")
        return

    start_index = page * BUTTONS_PER_PAGE
    end_index = start_index + BUTTONS_PER_PAGE
    recipes_page = recipes_in_category[start_index:end_index]

    keyboard = [[InlineKeyboardButton(f"🍽 {recipe['title']}", callback_data=f'recipe_{category}_{i + start_index}')] for i, recipe in enumerate(recipes_page)]
    if end_index < len(recipes_in_category):
        keyboard.append([InlineKeyboardButton("➡️ Следующая страница", callback_data=f'category_{category}_{page + 1}')])
    if page > 0:
        keyboard.append([InlineKeyboardButton("⬅️ Предыдущая страница", callback_data=f'category_{category}_{page - 1}')])

    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.message.edit_text("Выберите рецепт:", reply_markup=reply_markup)

async def recipe_button(update: Update, context: CallbackContext):
    query = update.callback_query
    await query.answer()

    data = query.data.split('_')
    category = data[1]
    recipe_index = int(data[2])
    recipes_in_category = [recipe for recipe in recipes if categorize_recipe(recipe['title']) == category]

    if 0 <= recipe_index < len(recipes_in_category):
        recipe = recipes_in_category[recipe_index]
        recipe_text = format_recipe(recipe)

        await query.message.delete()
        await query.message.reply_text(recipe_text, parse_mode='Markdown')

        keyboard = [[InlineKeyboardButton(f"{CATEGORY_EMOJIS.get(cat, '🍴')} {cat}", callback_data=f'category_{cat}_0')] for cat in get_categories(recipes)]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.message.reply_text("Выберите категорию рецептов:", reply_markup=reply_markup)
    else:
        await query.message.reply_text("Ошибка: Рецепт не найден.")

async def main():
    application = ApplicationBuilder().token("6953692387:AAEm-p8VtfqdmkHtbs8hxZWS-XNkdRN2lRE").build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CallbackQueryHandler(category_button, pattern='^category_'))
    application.add_handler(CallbackQueryHandler(recipe_button, pattern='^recipe_'))

    await application.initialize()
    await application.start()
    await application.updater.start_polling()
    await asyncio.Event().wait()

async def run_bot():
    while True:
        try:
            await main()
        except Exception as e:
            logging.error(f"Ошибка: {e}")
            await asyncio.sleep(10)  # Пауза перед перезапуском

if __name__ == '__main__':
    asyncio.run(run_bot())
