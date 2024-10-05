import logging
import json
import asyncio
import aiohttp
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CallbackContext, CommandHandler, CallbackQueryHandler

# Логирование
logging.basicConfig(level=logging.INFO)

# Функция для загрузки рецептов из файлов
async def load_recipes():
    recipes = []
    urls = [
        "https://raw.githubusercontent.com/Ioneovv/CheffBot/main/recipes_part1.json",
        "https://raw.githubusercontent.com/Ioneovv/CheffBot/main/recipes_part2.json"
    ]

    async with aiohttp.ClientSession() as session:
        for url in urls:
            async with session.get(url) as response:
                if response.status == 200:
                    data = await response.json()
                    recipes.extend(data)
                    print(f"Файл {url} загружен успешно!")
                else:
                    print(f"Ошибка загрузки {url}: {response.status}")
    return recipes

# Загружаем рецепты
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

# Команда для показа избранного
async def show_favorites(update: Update, context: CallbackContext):
    user_id = update.effective_user.id
    favorites = user_data.get(user_id, {}).get('favorites', [])

    if favorites:
        message = "Ваши избранные рецепты:\n\n" + "\n".join(f"🍽 {r['title']}" for r in favorites)
    else:
        message = "У вас пока нет избранных рецептов."

    await update.message.reply_text(message)

# Поиск рецептов по ингредиентам
async def search_recipes(update: Update, context: CallbackContext):
    query = ' '.join(context.args)
    matched_recipes = [r for r in recipes if any(query.lower() in i.lower() for i in r.get('ingredients', []))]

    if matched_recipes:
        result = "Найденные рецепты:\n\n" + "\n".join(f"🍽 {r['title']}" for r in matched_recipes)
    else:
        result = "Рецептов по вашим ингредиентам не найдено."

    await update.message.reply_text(result)

# Добавление рецептов в избранное
async def add_to_favorites(update: Update, context: CallbackContext):
    user_id = update.effective_user.id
    query = update.callback_query
    recipe_index = int(query.data.split('_')[2])

    recipe = recipes[recipe_index]
    if recipe not in user_data[user_id]['favorites']:
        user_data[user_id]['favorites'].append(recipe)
        await query.answer("Рецепт добавлен в избранное!")
    else:
        await query.answer("Рецепт уже в избранном!")

# Рейтинг рецептов
async def rate_recipe(update: Update, context: CallbackContext):
    query = update.callback_query
    recipe_index = int(query.data.split('_')[2])
    rating = int(query.data.split('_')[3])

    recipes[recipe_index]['rating'] = rating
    await query.answer(f"Вы оценили рецепт на {rating} звёзд!")

# История просмотров
async def show_history(update: Update, context: CallbackContext):
    user_id = update.effective_user.id
    history = user_data.get(user_id, {}).get('history', [])

    if history:
        message = "Ваша история просмотров:\n\n" + "\n".join(f"🍽 {r['title']}" for r in history)
    else:
        message = "История просмотров пуста."

    await update.message.reply_text(message)

# Основная логика (категории, рецепты)
async def category_button(update: Update, context: CallbackContext):
    query = update.callback_query
    category = query.data.split('_')[1]

    recipes_in_category = [recipe for recipe in recipes if recipe.get('category') == category]
    if recipes_in_category:
        keyboard = [[InlineKeyboardButton(f"🍽 {recipe['title']}", callback_data=f'recipe_{i}')] for i, recipe in enumerate(recipes_in_category)]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.message.edit_text("Выберите рецепт:", reply_markup=reply_markup)

# Показывать рецепт
async def show_recipe(update: Update, context: CallbackContext):
    query = update.callback_query
    recipe_index = int(query.data.split('_')[1])

    recipe = recipes[recipe_index]
    recipe_text = f"🍽 **{recipe['title']}**\n\nИнгредиенты:\n" + "\n".join(f"- {i}" for i in recipe.get('ingredients', [])) + "\n\nПриготовление:\n" + "\n".join(f"{i+1}. {s}" for i, s in enumerate(recipe.get('instructions', [])))

    user_id = update.effective_user.id
    user_data[user_id]['history'].append(recipe)

    await query.message.reply_text(recipe_text)

# Команда /menu для навигации
async def menu(update: Update, context: CallbackContext):
    keyboard = [
        [InlineKeyboardButton("Избранное", callback_data='show_favorites')],
        [InlineKeyboardButton("История", callback_data='show_history')],
        [InlineKeyboardButton("Поиск по ингредиентам", callback_data='search')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("Меню", reply_markup=reply_markup)

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
