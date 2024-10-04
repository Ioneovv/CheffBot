import logging
import random
import sqlite3
import json
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CallbackContext, CommandHandler, CallbackQueryHandler

# Логирование
logging.basicConfig(level=logging.INFO)

# База данных SQLite
conn = sqlite3.connect('recipes.db', check_same_thread=False)
c = conn.cursor()

# Создание таблиц
c.execute('''CREATE TABLE IF NOT EXISTS recipes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT,
    category TEXT,
    ingredients TEXT,
    instructions TEXT
)''')
c.execute('''CREATE TABLE IF NOT EXISTS feedback (
    recipe_id INTEGER,
    user_id INTEGER,
    comment TEXT,
    FOREIGN KEY(recipe_id) REFERENCES recipes(id)
)''')
conn.commit()

# Список категорий
CATEGORIES = ["Завтраки", "Основные блюда", "Салаты", "Супы", "Десерты", "Закуски"]

# Функция для загрузки рецептов из базы данных
def load_recipes():
    c.execute('SELECT * FROM recipes')
    return c.fetchall()

# Функция для получения категорий
def get_categories():
    return CATEGORIES

# Форматирование рецепта
def format_recipe(recipe):
    title, ingredients, instructions = recipe[1], recipe[3], recipe[4]
    text = f"🍽 **{title}**\n\n"
    text += "📝 **Ингредиенты:**\n"
    text += f"{ingredients}\n\n"
    text += "🧑‍🍳 **Приготовление:**\n"
    text += f"{instructions}"
    return text

# Команда старта
async def start(update: Update, context: CallbackContext):
    user_id = update.effective_user.id
    username = update.effective_user.username
    categories = get_categories()

    # Приветственное сообщение
    await update.message.reply_text(f'Привет, {username}! Выберите категорию рецептов:')

    # Кнопки категорий
    keyboard = [[InlineKeyboardButton(category, callback_data=f'category_{category}')] for category in categories]
    keyboard.append([InlineKeyboardButton("🎲 Случайный рецепт", callback_data='random_recipe')])
    keyboard.append([InlineKeyboardButton("📅 Меню на неделю", callback_data='weekly_menu')])
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("Что бы вы хотели приготовить сегодня?", reply_markup=reply_markup)

# Обработка нажатий на кнопки категорий
async def category_button(update: Update, context: CallbackContext):
    query = update.callback_query
    await query.answer()
    category = query.data.split('_')[1]

    # Получаем рецепты из выбранной категории
    c.execute('SELECT * FROM recipes WHERE category = ?', (category,))
    recipes_in_category = c.fetchall()

    # Кнопки с рецептами
    keyboard = [[InlineKeyboardButton(recipe[1], callback_data=f'recipe_{recipe[0]}')] for recipe in recipes_in_category]
    keyboard.append([InlineKeyboardButton("Назад", callback_data='back_to_categories')])
    reply_markup = InlineKeyboardMarkup(keyboard)

    await query.message.edit_text(f'Рецепты в категории {category}:', reply_markup=reply_markup)

# Обработка нажатий на кнопки с рецептами
async def recipe_button(update: Update, context: CallbackContext):
    query = update.callback_query
    await query.answer()
    recipe_id = int(query.data.split('_')[1])

    # Получаем рецепт по ID
    c.execute('SELECT * FROM recipes WHERE id = ?', (recipe_id,))
    recipe = c.fetchone()

    # Форматируем рецепт
    recipe_text = format_recipe(recipe)

    # Кнопки для действия с рецептом
    keyboard = [
        [InlineKeyboardButton("Оставить отзыв", callback_data=f'feedback_{recipe_id}')],
        [InlineKeyboardButton("Назад к списку", callback_data='back_to_categories')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await query.message.edit_text(recipe_text, reply_markup=reply_markup)

# Случайный рецепт
async def random_recipe(update: Update, context: CallbackContext):
    query = update.callback_query
    await query.answer()

    c.execute('SELECT * FROM recipes ORDER BY RANDOM() LIMIT 1')
    recipe = c.fetchone()

    recipe_text = format_recipe(recipe)
    keyboard = [
        [InlineKeyboardButton("Оставить отзыв", callback_data=f'feedback_{recipe[0]}')],
        [InlineKeyboardButton("Назад", callback_data='back_to_categories')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await query.message.edit_text(f"🎲 Вот случайный рецепт для вас:\n\n{recipe_text}", reply_markup=reply_markup)

# Меню на неделю
async def weekly_menu(update: Update, context: CallbackContext):
    query = update.callback_query
    await query.answer()

    c.execute('SELECT * FROM recipes ORDER BY RANDOM() LIMIT 7')
    weekly_recipes = c.fetchall()

    menu_text = "📅 **Меню на неделю**\n\n"
    for day, recipe in enumerate(weekly_recipes, 1):
        menu_text += f"День {day}: {recipe[1]}\n"

    await query.message.edit_text(menu_text)

# Обратная связь
async def feedback(update: Update, context: CallbackContext):
    query = update.callback_query
    await query.answer()
    recipe_id = int(query.data.split('_')[1])

    await query.message.reply_text(f"Введите свой отзыв для рецепта {recipe_id}:")

    # Здесь можно обработать и сохранить отзыв в базу данных

# Главная функция
def main():
    # Создаем бота
    app = ApplicationBuilder().token('6953692387:AAEm-p8VtfqdmkHtbs8hxZWS-XNkdRN2lRE').build()

    # Обработчики команд и кнопок
    app.add_handler(CommandHandler('start', start))
    app.add_handler(CallbackQueryHandler(category_button, pattern='^category_'))
    app.add_handler(CallbackQueryHandler(recipe_button, pattern='^recipe_'))
    app.add_handler(CallbackQueryHandler(random_recipe, pattern='^random_recipe$'))
    app.add_handler(CallbackQueryHandler(weekly_menu, pattern='^weekly_menu$'))
    app.add_handler(CallbackQueryHandler(feedback, pattern='^feedback_'))

    # Запуск бота
    app.run_polling()

if __name__ == '__main__':
    main()
