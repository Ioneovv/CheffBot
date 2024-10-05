import logging
import re
import requests
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CallbackContext, CommandHandler, CallbackQueryHandler
import asyncio
import random
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas

# Логирование
logging.basicConfig(level=logging.INFO)

# Прямая ссылка для загрузки рецептов
RECIPE_URL = 'https://drive.google.com/uc?id=1xHKBF9dBVJBqeO-tT6CxCgAx34TG46em'

# Глобальная переменная для хранения рецептов
recipes = []

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

# Словарь для избранных рецептов
user_favorites = {}

def load_recipes():
    try:
        response = requests.get(RECIPE_URL)
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        logging.error(f"Ошибка загрузки рецептов: {e}")
        return []
    except ValueError as e:
        logging.error(f"Ошибка обработки JSON: {e}")
        return []

def get_categories():
    categories = set(recipe.get('category') for recipe in recipes)
    return sorted(categories)

def format_recipe(recipe, servings=1):
    recipe_text = f"🍽 **{recipe['title']}**\n\n"
    recipe_text += "📝 **Ингредиенты:**\n"
    for ingredient in recipe.get('ingredients', []):
        amount = ingredient.get('amount', '')
        recipe_text += f"🔸 {ingredient['ingredient']:20} {amount * servings}\n"
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
    return "Неизвестно"

# Команда старт
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

# Поиск рецептов по ингредиентам
async def search_recipes(update: Update, context: CallbackContext):
    query = update.message.text.split(' ', 1)
    if len(query) < 2:
        await update.message.reply_text("Пожалуйста, укажите ингредиенты для поиска.")
        return

    ingredient = query[1].lower()
    matching_recipes = [recipe for recipe in recipes if ingredient in [ing['ingredient'].lower() for ing in recipe.get('ingredients', [])]]

    if not matching_recipes:
        await update.message.reply_text("Рецепты не найдены.")
        return

    await update.message.reply_text("Найдены рецепты:")
    for recipe in matching_recipes:
        await update.message.reply_text(recipe['title'])

# Случайный рецепт
async def random_recipe(update: Update, context: CallbackContext):
    if not recipes:
        await update.message.reply_text("Рецепты не загружены.")
        return
    recipe = random.choice(recipes)
    recipe_text = format_recipe(recipe)
    await update.message.reply_text(recipe_text, parse_mode='Markdown')

# Добавление в избранное
async def add_to_favorites(update: Update, context: CallbackContext):
    user_id = update.message.from_user.id
    recipe_index = int(context.args[0])
    if user_id not in user_favorites:
        user_favorites[user_id] = []
    user_favorites[user_id].append(recipe_index)
    await update.message.reply_text("Рецепт добавлен в избранное.")

# Показ избранных рецептов
async def show_favorites(update: Update, context: CallbackContext):
    user_id = update.message.from_user.id
    if user_id not in user_favorites or not user_favorites[user_id]:
        await update.message.reply_text("Избранные рецепты пусты.")
        return
    for index in user_favorites[user_id]:
        await update.message.reply_text(recipes[index]['title'])

# Кастомизация порций
async def customize_servings(update: Update, context: CallbackContext):
    recipe_index = int(context.args[0])  # Индекс рецепта
    servings = int(context.args[1]) if len(context.args) > 1 else 1
    recipe = recipes[recipe_index]
    recipe_text = format_recipe(recipe, servings)
    await update.message.reply_text(recipe_text, parse_mode='Markdown')

# Экспорт рецепта в PDF
async def export_recipe(update: Update, context: CallbackContext):
    recipe_index = int(context.args[0])
    recipe = recipes[recipe_index]
    pdf_file = f"{recipe['title']}.pdf"
    c = canvas.Canvas(pdf_file, pagesize=letter)
    c.drawString(100, 750, f"Рецепт: {recipe['title']}")
    # Добавьте остальные детали рецепта
    c.save()
    await update.message.reply_document(open(pdf_file, 'rb'))

# Категория
async def category_button(update: Update, context: CallbackContext):
    query = update.callback_query
    await query.answer()
    data = query.data.split('_')
    category = data[1]
    page = int(data[2])

    recipes_in_category = [recipe for recipe in recipes if categorize_recipe(recipe['title']) == category]
    start_index = page * BUTTONS_PER_PAGE
    end_index = start_index + BUTTONS_PER_PAGE
    buttons = []
    for i, recipe in enumerate(recipes_in_category[start_index:end_index], start=start_index):
        buttons.append([InlineKeyboardButton(recipe['title'], callback_data=f"recipe_{i}")])

    # Добавляем кнопки навигации
    nav_buttons = []
    if start_index > 0:
        nav_buttons.append(InlineKeyboardButton("Назад", callback_data=f"category_{category}_{page-1}"))
    if end_index < len(recipes_in_category):
        nav_buttons.append(InlineKeyboardButton("Вперед", callback_data=f"category_{category}_{page+1}"))
    if nav_buttons:
        buttons.append(nav_buttons)

    reply_markup = InlineKeyboardMarkup(buttons)
    await query.edit_message_text(f"Рецепты в категории: {category}", reply_markup=reply_markup)

# Обработка рецепта
async def recipe_button(update: Update, context: CallbackContext):
    query = update.callback_query
    await query.answer()
    recipe_index = int(query.data.split('_')[1])
    recipe = recipes[recipe_index]
    recipe_text = format_recipe(recipe)
    buttons = [
        [InlineKeyboardButton("Избранное", callback_data=f"favorite_{recipe_index}")],
        [InlineKeyboardButton("Экспорт в PDF", callback_data=f"export_{recipe_index}")]
    ]
    reply_markup = InlineKeyboardMarkup(buttons)
    await query.edit_message_text(recipe_text, parse_mode='Markdown', reply_markup=reply_markup)

# Обработчик команд
def main():
    application = ApplicationBuilder().token('6953692387:AAEm-p8VtfqdmkHtbs8hxZWS-XNkdRN2lRE').build()
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("search", search_recipes))
    application.add_handler(CommandHandler("random", random_recipe))
    application.add_handler(CommandHandler("favorite", add_to_favorites))
    application.add_handler(CommandHandler("favorites", show_favorites))
    application.add_handler(CommandHandler("servings", customize_servings))
    application.add_handler(CommandHandler("export", export_recipe))
    application.add_handler(CallbackQueryHandler(category_button, pattern=r'^category_'))
    application.add_handler(CallbackQueryHandler(recipe_button, pattern=r'^recipe_'))

    application.run_polling()

if __name__ == '__main__':
    main()
