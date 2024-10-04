import logging
import re
import requests
import sqlite3
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CallbackContext, CommandHandler, CallbackQueryHandler
import asyncio

# Логирование
logging.basicConfig(level=logging.INFO)

# Прямая ссылка для загрузки рецептов
RECIPE_URL = 'https://drive.google.com/uc?id=1xHKBF9dBVJBqeO-tT6CxCgAx34TG46em'

# Глобальная переменная для хранения рецептов
recipes = []
favorites = []

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

# Подключение к базе данных
conn = sqlite3.connect('users.db')
c = conn.cursor()
c.execute('''CREATE TABLE IF NOT EXISTS users (
    user_id INTEGER PRIMARY KEY,
    username TEXT
)''')
conn.commit()

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
    return "Неизвестно"

def add_user(user_id, username):
    c.execute('INSERT OR IGNORE INTO users (user_id, username) VALUES (?, ?)', (user_id, username))
    conn.commit()

def count_users():
    c.execute('SELECT COUNT(*) FROM users')
    return c.fetchone()[0]

async def start(update: Update, context: CallbackContext):
    global recipes
    recipes = load_recipes()
    if not recipes:
        await update.message.reply_text("Не удалось загрузить рецепты. Пожалуйста, попробуйте позже.")
        return

    user_id = update.effective_user.id
    username = update.effective_user.username

    add_user(user_id, username)  # Добавляем пользователя в базу
    user_count = count_users()    # Получаем количество пользователей

    await update.message.reply_text(f'Привет! Вы являетесь {user_count}-м пользователем этого бота!')

    categories = get_categories()
    keyboard = [[InlineKeyboardButton(f"{CATEGORY_EMOJIS.get(category, '🍴')} {category}", callback_data=f'category_{category}_0')] for category in categories]
    keyboard.append([InlineKeyboardButton("⭐️ Избранное", callback_data='favorites')])  # Кнопка избранного
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
    await query.message.edit_text(f'Рецепты в категории **{category}**:', reply_markup=reply_markup)

async def recipe_button(update: Update, context: CallbackContext):
    query = update.callback_query
    await query.answer()

    data = query.data.split('_')
    if len(data) != 3 or data[0] != 'recipe':
        await query.message.reply_text("Ошибка: Неверный индекс рецепта.")
        return

    category = data[1]
    recipe_index = int(data[2])
    recipe = recipes[recipe_index]

    if recipe:
        recipe_text = format_recipe(recipe)
        keyboard = [[InlineKeyboardButton("⭐️ Добавить в избранное", callback_data=f'add_favorite_{category}_{recipe_index}'), InlineKeyboardButton("На главную", callback_data='menu')]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.message.reply_text(recipe_text, reply_markup=reply_markup)
    else:
        await query.message.reply_text("Ошибка: Рецепт не найден.")

async def add_favorite(update: Update, context: CallbackContext):
    query = update.callback_query
    await query.answer()

    data = query.data.split('_')
    if len(data) != 3 or data[0] != 'add_favorite':
        await query.message.reply_text("Ошибка: Неверные данные для добавления в избранное.")
        return

    recipe_index = int(data[2])
    recipe = recipes[recipe_index]

    if recipe:
        favorites.append(recipe)
        await query.message.reply_text(f"✅ Рецепт **{recipe['title']}** добавлен в Избранное!")
    else:
        await query.message.reply_text("Ошибка: Рецепт не найден.")

async def show_favorites(update: Update, context: CallbackContext):
    if not favorites:
        await update.message.reply_text("Избранное пусто.")
        return

    favorites_text = "⭐️ Избранные рецепты:\n\n"
    for i, recipe in enumerate(favorites):
        favorites_text += f"{i + 1}. {recipe['title']}\n"

    await update.message.reply_text(favorites_text)

async def menu(update: Update, context: CallbackContext):
    query = update.callback_query  # Получаем объект callback_query
    await query.answer()  # Обязательно отвечаем на запрос

    categories = get_categories()
    keyboard = [[InlineKeyboardButton(f"{CATEGORY_EMOJIS.get(category, '🍴')} {category}", callback_data=f'category_{category}_0')] for category in categories]
    keyboard.append([InlineKeyboardButton("⭐️ Избранное", callback_data='favorites')])  # Кнопка избранного
    reply_markup = InlineKeyboardMarkup(keyboard)

    await query.message.edit_text('Выберите категорию рецептов:', reply_markup=reply_markup)  # Изменяем текст сообщения

def main():
    app = ApplicationBuilder().token('6953692387:AAEm-p8VtfqdmkHtbs8hxZWS-XNkdRN2lRE').build()

    app.add_handler(CommandHandler('start', start))
    app.add_handler(CallbackQueryHandler(category_button, pattern=r'category_'))
    app.add_handler(CallbackQueryHandler(recipe_button, pattern=r'recipe_'))
    app.add_handler(CallbackQueryHandler(add_favorite, pattern=r'add_favorite_'))
    app.add_handler(CallbackQueryHandler(show_favorites, pattern=r'favorites'))
    app.add_handler(CallbackQueryHandler(menu, pattern=r'menu'))  # Добавляем обработчик для меню

    app.run_polling()

if __name__ == '__main__':
    recipes = load_recipes()
    main()
