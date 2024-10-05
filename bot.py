import logging
import json
import re
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CallbackContext, CommandHandler, CallbackQueryHandler
import asyncio

# Логирование
logging.basicConfig(level=logging.INFO)

# Путь к файлу с рецептами
RECIPE_FILE = 'recipes_part1.json'

# Глобальная переменная для хранения рецептов
recipes = []
favorites = []
usage_stats = {}

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
    """Загрузка рецептов из файла JSON"""
    try:
        with open(RECIPE_FILE, 'r', encoding='utf-8') as file:
            return json.load(file)
    except (FileNotFoundError, json.JSONDecodeError) as e:
        logging.error(f"Ошибка загрузки рецептов: {e}")
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
        
        if len(data) != 3:
            await query.message.reply_text("Ошибка: Неверные данные кнопки.")
            return

        category = data[1]
        recipe_index = int(data[2])
        recipes_in_category = [recipe for recipe in recipes if categorize_recipe(recipe['title']) == category]

        if 0 <= recipe_index < len(recipes_in_category):
            recipe = recipes_in_category[recipe_index]
            recipe_text = format_recipe(recipe)

            # Увеличиваем счетчик использования
            usage_stats[recipe['title']] = usage_stats.get(recipe['title'], 0) + 1

            await query.message.delete()
            await query.message.reply_text(recipe_text, parse_mode='Markdown')

            # Формируем клавиатуру с ограничением на количество кнопок в строке
            keyboard = []
            category_buttons = [
                InlineKeyboardButton(f"{CATEGORY_EMOJIS.get(cat, '🍴')} {cat}", callback_data=f'category_{cat}_0') 
                for cat in get_categories()
            ]

            # Добавляем кнопки категорий по 2 в строку
            for i in range(0, len(category_buttons), 2):
                keyboard.append(category_buttons[i:i + 2])

            keyboard.append([InlineKeyboardButton("⭐️ Добавить в избранное", callback_data=f'add_favorite_{recipe["title"]}')])
            keyboard.append([InlineKeyboardButton("⭐️ Избранное", callback_data='favorites')])
            keyboard.append([InlineKeyboardButton("📊 Статистика", callback_data='stats')])

            reply_markup = InlineKeyboardMarkup(keyboard)
            await query.message.reply_text("Выберите действие:", reply_markup=reply_markup)
        else:
            await query.message.reply_text("Ошибка: Рецепт не найден.")
    except Exception as e:
        logging.error(f"Ошибка в обработчике кнопки рецепта: {e}")
        await query.message.reply_text("Произошла ошибка. Пожалуйста, попробуйте позже.")

async def add_to_favorites(update: Update, context: CallbackContext):
    query = update.callback_query
    await query.answer()
    recipe_title = query.data.split('_')[2]

    if recipe_title not in favorites:
        favorites.append(recipe_title)
        await query.message.reply_text(f"Рецепт '{recipe_title}' добавлен в избранное.")
    else:
        await query.message.reply_text(f"Рецепт '{recipe_title}' уже в избранном.")

async def view_favorites(update: Update, context: CallbackContext):
    query = update.callback_query
    await query.answer()

    if not favorites:
        await query.message.reply_text("Ваши избранные рецепты пусты.")
        return

    favorites_text = "⭐️ Избранные рецепты:\n\n"
    for recipe_title in favorites:
        favorites_text += f"- {recipe_title}\n"

    await query.message.reply_text(favorites_text)

async def view_stats(update: Update, context: CallbackContext):
    query = update.callback_query
    await query.answer()

    if not usage_stats:
        await query.message.reply_text("Нет данных о использовании.")
        return

    stats_text = "📊 Статистика использования рецептов:\n\n"
    for title, count in usage_stats.items():
        stats_text += f"📝 {title}: {count} раз(а)\n"

    await query.message.reply_text(stats_text)

def main():
    application = ApplicationBuilder().token('6953692387:AAEm-p8VtfqdmkHtbs8hxZWS-XNkdRN2lRE').build()

    # Обработчики команд
    application.add_handler(CommandHandler("start", start))

    # Обработчики кнопок
    application.add_handler(CallbackQueryHandler(category_button, pattern=r'category_\w+_\d+'))
    application.add_handler(CallbackQueryHandler(recipe_button, pattern=r'recipe_\w+_\d+'))
    application.add_handler(CallbackQueryHandler(add_to_favorites, pattern=r'add_favorite_\w+'))
    application.add_handler(CallbackQueryHandler(view_favorites, pattern=r'favorites'))
    application.add_handler(CallbackQueryHandler(view_stats, pattern=r'stats'))

    application.run_polling()

if __name__ == '__main__':
    main()
