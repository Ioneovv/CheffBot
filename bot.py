import json
import random
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

# Функция для загрузки рецептов
async def load_recipes():
    try:
        with open('recipes.json', 'r', encoding='utf-8') as file:
            recipes = json.load(file)
            return recipes
    except Exception as e:
        print(f"Ошибка загрузки или обработки recipes.json: {e}")
        return {}

# Функция для отправки случайного рецепта
async def random_recipe(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    recipes = await load_recipes()
    recipe = random.choice(list(recipes.values()))
    await update.message.reply_text(
        f"🍽️ **{recipe['name']}**\n\n{recipe['description']}\n\n**Ингредиенты:**\n{recipe['ingredients']}\n\n**Приготовление:**\n{recipe['instructions']}",
        parse_mode='Markdown'
    )

# Функция для поиска рецептов по названию
async def search_recipe(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    recipes = await load_recipes()
    query = update.message.text.lower()
    found_recipes = [r for r in recipes.values() if query in r['name'].lower()]
    
    if found_recipes:
        response = '\n\n'.join([f"🍽️ **{r['name']}**\n{r['description']}" for r in found_recipes])
        await update.message.reply_text(response, parse_mode='Markdown')
    else:
        await update.message.reply_text("❌ Рецепты не найдены. Попробуйте другой запрос.")

# Функция для начала общения с ботом
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user = update.effective_user
    keyboard = [
        [InlineKeyboardButton("Случайный рецепт 🍲", callback_data='random_recipe')],
        [InlineKeyboardButton("Поиск рецепта 🔍", callback_data='search_recipe')],
        [InlineKeyboardButton("Помощь ❓", callback_data='help')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_html(
        rf"Привет, {user.mention_html()}! Добро пожаловать в CheffBot! Выберите действие:",
        reply_markup=reply_markup
    )

# Функция для обработки нажатий кнопок
async def button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if query.data == 'random_recipe':
        await random_recipe(query.message, context)
    elif query.data == 'search_recipe':
        await query.message.reply_text("Введите название рецепта, чтобы найти его.")
    elif query.data == 'help':
        await query.message.reply_text(
            "Доступные команды:\n/start - Запустить бота\n/help - Помощь\n/random - Получить случайный рецепт\nВведите название рецепта, чтобы найти его."
        )

# Основная функция для запуска бота
async def main() -> None:
    app = Application.builder().token("YOUR_BOT_TOKEN").build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", lambda update, context: update.message.reply_text("Используйте /start для запуска бота.")))
    app.add_handler(CommandHandler("random", random_recipe))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, search_recipe))
    app.add_handler(MessageHandler(filters.COMMAND, lambda update, context: update.message.reply_text("Пожалуйста, используйте кнопки.")))

    await app.run_polling()

# Запуск бота
if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
