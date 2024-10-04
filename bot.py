import logging
import re
import requests
import sqlite3
import json
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CallbackContext, CommandHandler, CallbackQueryHandler
import random

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

def load_feedback():
    try:
        with open('data.json', 'r', encoding='utf-8') as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {}

def save_feedback(feedback):
    with open('data.json', 'w', encoding='utf-8') as f:
        json.dump(feedback, f, ensure_ascii=False, indent=4)

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
    keyboard.append([InlineKeyboardButton("📅 Составить меню на неделю", callback_data='weekly_menu')])
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

    keyboard = [[InlineKeyboardButton(recipe['title'], callback_data=f'recipe_{recipes.index(recipe)}')] for recipe in recipes_page]

    if start_index > 0:
        keyboard.append([InlineKeyboardButton("Назад", callback_data=f'category_{category}_{page - 1}')])
    if end_index < len(recipes_in_category):
        keyboard.append([InlineKeyboardButton("Вперед", callback_data=f'category_{category}_{page + 1}')])

    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.message.edit_text(f"Рецепты категории: {category}", reply_markup=reply_markup)

async def recipe_button(update: Update, context: CallbackContext):
    query = update.callback_query
    await query.answer()

    recipe_index = int(query.data.split('_')[1])
    if recipe_index < 0 or recipe_index >= len(recipes):
        await query.message.reply_text("Ошибка: Индекс рецепта вне диапазона.")
        return

    recipe = recipes[recipe_index]
    recipe_text = format_recipe(recipe)

    # Кнопки для обратной связи
    feedback_keyboard = [
        [InlineKeyboardButton("✅ Хорошо", callback_data=f'feedback_{recipe_index}_good')],
        [InlineKeyboardButton("❌ Плохо", callback_data=f'feedback_{recipe_index}_bad')]
    ]
    reply_markup = InlineKeyboardMarkup(feedback_keyboard)

    await query.message.edit_text(recipe_text, reply_markup=reply_markup)

async def handle_feedback(update: Update, context: CallbackContext):
    query = update.callback_query
    await query.answer()

    data = query.data.split('_')
    recipe_index = int(data[1])
    feedback = data[2]

    user_feedback = load_feedback()
    if str(recipe_index) not in user_feedback:
        user_feedback[str(recipe_index)] = []
    
    user_feedback[str(recipe_index)].append(feedback)
    save_feedback(user_feedback)

    await query.message.reply_text("Спасибо за ваш отзыв!")

async def weekly_menu(update: Update, context: CallbackContext):
    await update.callback_query.answer()

    # Выбор количества блюд
    keyboard = [
        [InlineKeyboardButton("7 блюд", callback_data='menu_7')],
        [InlineKeyboardButton("14 блюд", callback_data='menu_14')],
        [InlineKeyboardButton("21 блюдо", callback_data='menu_21')],
        [InlineKeyboardButton("⬅️ Назад", callback_data='back_to_categories')]
    ]
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.callback_query.message.edit_text("Сколько блюд вы хотите в меню на неделю?", reply_markup=reply_markup)

async def generate_weekly_menu(update: Update, context: CallbackContext):
    query = update.callback_query
    await query.answer()

    # Получаем количество блюд из данных кнопки
    number_of_meals = int(query.data.split('_')[1])
    
    # Случайный выбор рецептов
    selected_recipes = random.sample(recipes, min(number_of_meals, len(recipes)))

    # Форматирование меню
    menu_text = "🍽 **Ваше меню на неделю:**\n\n"
    for i, recipe in enumerate(selected_recipes, start=1):
        menu_text += f"{i}. **{recipe['title']}**\n"

    # Отправляем меню пользователю
    await query.message.edit_text(menu_text)

async def back_to_categories(update: Update, context: CallbackContext):
    await start(update, context)

def main():
    application = ApplicationBuilder().token("6953692387:AAEm-p8VtfqdmkHtbs8hxZWS-XNkdRN2lRE").build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CallbackQueryHandler(category_button, pattern=r'^category_'))
    application.add_handler(CallbackQueryHandler(recipe_button, pattern=r'^recipe_'))
    application.add_handler(CallbackQueryHandler(handle_feedback, pattern=r'^feedback_'))
    application.add_handler(CallbackQueryHandler(weekly_menu, pattern=r'^weekly_menu$'))
    application.add_handler(CallbackQueryHandler(generate_weekly_menu, pattern=r'^menu_'))
    application.add_handler(CallbackQueryHandler(back_to_categories, pattern=r'^back_to_categories$'))

    application.run_polling()

if __name__ == '__main__':
    recipes = load_recipes()  # Загрузите рецепты при запуске
    main()
