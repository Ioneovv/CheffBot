import logging
import re
import requests
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CallbackContext, CommandHandler, CallbackQueryHandler
import asyncio
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
import io

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

# Избранные рецепты
favorites = []

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

async def start(update: Update, context: CallbackContext):
    global recipes
    recipes = load_recipes()
    if not recipes:
        await update.message.reply_text("Не удалось загрузить рецепты. Пожалуйста, попробуйте позже.")
        return

    categories = get_categories()
    keyboard = [[InlineKeyboardButton(f"{CATEGORY_EMOJIS.get(category, '🍴')} {category}", callback_data=f'category_{category}_0')] for category in categories]
    reply_markup = InlineKeyboardMarkup(keyboard)

    if update.message:
        await update.message.reply_text('Выберите категорию рецептов:', reply_markup=reply_markup)
    elif update.callback_query:
        await update.callback_query.message.edit_text('Выберите категорию рецептов:', reply_markup=reply_markup)

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

    keyboard.append([InlineKeyboardButton("🏠 Домой", callback_data='home')])

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

            buttons = [
                [InlineKeyboardButton("⭐ Добавить в избранное", callback_data=f"favorite_{recipe_index}")],
                [InlineKeyboardButton("📄 Экспорт в PDF", callback_data=f"export_{recipe_index}")],
                [InlineKeyboardButton("🏠 Домой", callback_data='home')],
                [InlineKeyboardButton("⬅️ Назад", callback_data=f'category_{category}_0')]
            ]
            reply_markup = InlineKeyboardMarkup(buttons)
            await query.message.delete()
            await query.message.reply_text(recipe_text, parse_mode='Markdown', reply_markup=reply_markup)
        else:
            await query.message.reply_text("Ошибка: Рецепт не найден.")
    except Exception as e:
        logging.error(f"Ошибка в обработчике кнопки рецепта: {e}")
        await query.message.reply_text("Произошла ошибка. Попробуйте снова.")

async def favorite_button(update: Update, context: CallbackContext):
    query = update.callback_query
    await query.answer()

    recipe_index = int(query.data.split('_')[1])
    if recipe_index in favorites:
        favorites.remove(recipe_index)
        await query.message.reply_text("Рецепт удален из избранного.")
    else:
        favorites.append(recipe_index)
        await query.message.reply_text("Рецепт добавлен в избранное.")

async def show_favorites(update: Update, context: CallbackContext):
    if not favorites:
        await update.message.reply_text("Ваш список избранного пуст.")
        return

    fav_recipes = [recipes[i] for i in favorites]
    message = "⭐ **Избранные рецепты**\n\n" + "\n".join([f"{i+1}. {recipe['title']}" for i, recipe in enumerate(fav_recipes)])
    await update.message.reply_text(message)

async def export_to_pdf(update: Update, context: CallbackContext):
    query = update.callback_query
    await query.answer()
    recipe_index = int(query.data.split('_')[1])
    recipe = recipes[recipe_index]

    buffer = io.BytesIO()
    c = canvas.Canvas(buffer, pagesize=letter)
    c.drawString(100, 750, recipe['title'])
    y = 700
    for ingredient in recipe['ingredients']:
        c.drawString(100, y, f"{ingredient['ingredient']}: {ingredient.get('amount', '')}")
        y -= 20

    y -= 20
    for i, step in enumerate(recipe['instructions'], start=1):
        c.drawString(100, y, f"{i}. {step}")
        y -= 20

    c.showPage()
    c.save()
    buffer.seek(0)
    await query.message.reply_document(document=buffer, filename=f"{recipe['title']}.pdf")

async def home(update: Update, context: CallbackContext):
    # Обрабатываем случай, когда функция вызывается из callback_query
    if update.callback_query:
        await start(update, context)

def main():
    # Создание экземпляра бота
    app = ApplicationBuilder().token("6953692387:AAEm-p8VtfqdmkHtbs8hxZWS-XNkdRN2lRE").build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("favorites", show_favorites))
    app.add_handler(CallbackQueryHandler(category_button, pattern=r'^category_'))
    app.add_handler(CallbackQueryHandler(recipe_button, pattern=r'^recipe_'))
    app.add_handler(CallbackQueryHandler(favorite_button, pattern=r'^favorite_'))
    app.add_handler(CallbackQueryHandler(export_to_pdf, pattern=r'^export_'))
    app.add_handler(CallbackQueryHandler(home, pattern='^home'))

    # Запуск бота
    app.run_polling()

if __name__ == '__main__':
    main()
