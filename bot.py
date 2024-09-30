import logging 
import re
import requests
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CallbackContext, CommandHandler, CallbackQueryHandler, MessageHandler, filters
import asyncio

# Логирование
logging.basicConfig(level=logging.INFO)

# Прямая ссылка для загрузки рецептов
RECIPE_URL = 'https://drive.google.com/uc?id=1xHKBF9dBVJBqeO-tT6CxCgAx34TG46em'

# Глобальная переменная для хранения рецептов
recipes = []
favorite_recipes = []  # Для хранения избранных рецептов

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
    'Салаты': ['салат', 'зелёный', 'овощной', 'капустный', 'винегрет', 'греческий', 'цезарь'],
    'Супы': ['суп', 'бульон', 'щавель', 'крем-суп', 'рассольник', 'окрошка', 'пюре', 'пельмени'],
    'Десерты': ['торт', 'пирог', 'печенье', 'пудинг', 'десерт', 'мороженое', 'запеканка', 'творожное'],
    'Тесто': ['тесто', 'пирог', 'блины', 'блинчики', 'кекс', 'маффин', 'выпечка', 'пицца'],
    'Хлеб': ['хлеб', 'булочка', 'круассан', 'багет', 'лебедушка', 'пита', 'фокачча'],
    'Основные блюда': ['мясо', 'рыба', 'паста', 'гриль', 'запеканка', 'жаркое'],
    'Закуски': ['закуска', 'канапе', 'кростини', 'фингер-фуд', 'рагу', 'кебаб'],
    'Напитки': ['напиток', 'смузи', 'коктейль', 'чай', 'кофе', 'сок', 'молочный коктейль'],
    'Вегетарианские': ['вегетарианский', 'веганский', 'овощи', 'тофу', 'сейтан'],
    'Диетические': ['диетический', 'низкокалорийный', 'обезжиренный', 'салат', 'овощной суп'],
    'Завтраки': ['завтрак', 'сырники', 'каша', 'омлет', 'яичница', 'блины', 'оладьи', 'гренки', 'пудинг', 'йогурт', 'смесь злаков', 'мюсли'],
    'Паста': ['спагетти', 'лазанья', 'спиральки', 'фарфале', 'карбонара', 'фитучини', 'ньоки', 'птим птим', 'орзо', 'ризотто', 'тельятели']
}

# Максимальное количество кнопок на странице
BUTTONS_PER_PAGE = 5

def load_recipes():
    try:
        response = requests.get(RECIPE_URL)
        response.raise_for_status()
        return response.json()
    except requests.HTTPError as e:
        logging.error(f"Ошибка HTTP: {e}")
        return []
    except requests.RequestException as e:
        logging.error(f"Ошибка загрузки рецептов: {e}")
        return []
    except ValueError as e:
        logging.error(f"Ошибка обработки JSON: {e}")
        return []

def get_categories():
    categories = set(recipe.get('category') for recipe in recipes if recipe.get('category'))
    return sorted(categories)

def format_recipe(recipe):
    recipe_text = f"🍽 **{recipe['title']}**\n\n"
    recipe_text += "📝 **Ингредиенты:**\n"
    for ingredient in recipe.get('ingredients', []):
        amount = ingredient.get('amount', '')
        recipe_text += f"🔸 {ingredient['ingredient']:20} {amount}\n"
    recipe_text += "\n🧑‍🍳 **Приготовление:**\n"
    for i, step in enumerate(recipe.get('instructions', []), start=1):
        recipe_text += f"{i}. {step}\n"
    return recipe_text

def categorize_recipe(recipe_title):
    """Поиск категории рецепта по ключевым словам"""
    for category, keywords in CATEGORIES.items():
        pattern = r'\b(?:' + '|'.join(re.escape(kw) for kw in keywords) + r')\b'
        if re.search(pattern, recipe_title, re.IGNORECASE):
            return category
    return None  # Вернуть None, если категория не найдена

async def start(update: Update, context: CallbackContext):
    global recipes
    recipes = load_recipes()
    if not recipes:
        await update.message.reply_text("Не удалось загрузить рецепты. Пожалуйста, попробуйте позже.")
        return

    categories = get_categories()
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

    try:
        data = query.data.split('_')
        category = data[1]
        recipe_index = int(data[2])
        recipes_in_category = [recipe for recipe in recipes if categorize_recipe(recipe['title']) == category]

        if 0 <= recipe_index < len(recipes_in_category):
            recipe = recipes_in_category[recipe_index]
            recipe_text = format_recipe(recipe)

            await query.message.delete()
            await query.message.reply_text(recipe_text, parse_mode='Markdown')

            keyboard = [[InlineKeyboardButton(f"{CATEGORY_EMOJIS.get(cat, '🍴')} {cat}", callback_data=f'category_{cat}_0')] for cat in get_categories()]
            reply_markup = InlineKeyboardMarkup(keyboard)
            await query.message.reply_text("Выберите категорию рецептов:", reply_markup=reply_markup)
        else:
            await query.message.reply_text("Ошибка: Рецепт не найден.")
    except Exception as e:
        logging.error(f"Ошибка в обработчике кнопки рецепта: {e}")
        await query.message.reply_text("Произошла ошибка. Попробуйте снова.")

async def add_to_favorites(update: Update, context: CallbackContext):
    query = update.callback_query
    await query.answer()

    data = query.data.split('_')
    category = data[1]
    recipe_index = int(data[2])

    recipes_in_category = [recipe for recipe in recipes if categorize_recipe(recipe['title']) == category]
    if 0 <= recipe_index < len(recipes_in_category):
        favorite_recipes.append(recipes_in_category[recipe_index])
        await query.message.reply_text("Рецепт добавлен в избранное.")
    else:
        await query.message.reply_text("Ошибка: Рецепт не найден.")

async def view_favorites(update: Update, context: CallbackContext):
    if not favorite_recipes:
        await update.message.reply_text("Ваши избранные рецепты пусты.")
        return

    favorites_text = "Ваши избранные рецепты:\n"
    for recipe in favorite_recipes:
        favorites_text += f"🍽 {recipe['title']}\n"

    await update.message.reply_text(favorites_text)

async def search_by_ingredient(update: Update, context: CallbackContext):
    query = update.message.text.split(maxsplit=1)
    if len(query) < 2:
        await update.message.reply_text("Введите ингредиент для поиска.")
        return

    ingredient = query[1].lower()
    found_recipes = [recipe for recipe in recipes if any(ingredient in ingredient['ingredient'].lower() for ingredient in recipe.get('ingredients', []))]

    if not found_recipes:
        await update.message.reply_text("Рецепты не найдены.")
        return

    search_results_text = "Рецепты, содержащие ингредиент:\n"
    for recipe in found_recipes:
        search_results_text += f"🍽 {recipe['title']}\n"

    await update.message.reply_text(search_results_text)

async def survey(update: Update, context: CallbackContext):
    await update.message.reply_text("Какой тип рецептов вы хотите видеть чаще? Напишите в ответном сообщении.")

async def handle_survey_response(update: Update, context: CallbackContext):
    response = update.message.text
    # Здесь можно сохранить или обработать ответ на опрос
    await update.message.reply_text(f"Спасибо за ваш ответ: '{response}'")

if __name__ == "__main__":
    app = ApplicationBuilder().token("6953692387:AAEm-p8VtfqdmkHtbs8hxZWS-XNkdRN2lRE").build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(category_button, pattern=r'category_'))
    app.add_handler(CallbackQueryHandler(recipe_button, pattern=r'recipe_'))
    app.add_handler(CallbackQueryHandler(add_to_favorites, pattern=r'add_favorite_'))
    app.add_handler(CommandHandler("favorites", view_favorites))
    app.add_handler(CommandHandler("search", search_by_ingredient))
    app.add_handler(CommandHandler("survey", survey))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_survey_response))

    app.run_polling()
