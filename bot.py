import json
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes

# Функция для загрузки рецептов из JSON-файла
async def load_recipes():
    try:
        with open('recipes.json', 'r', encoding='utf-8') as file:
            return json.load(file)
    except Exception as e:
        print(f"Ошибка загрузки или обработки recipes.json: {e}")
        return []

# Команда /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Добро пожаловать! Используйте /help для получения списка команд.")

# Команда /help
async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    help_text = (
        "Доступные команды:\n"
        "/start - Запустить бота\n"
        "/help - Помощь\n"
        "Введите название рецепта, чтобы найти его."
    )
    await update.message.reply_text(help_text)

# Поиск рецептов
async def search_recipes(update: Update, context: ContextTypes.DEFAULT_TYPE):
    recipes = await load_recipes()
    query = update.message.text.lower()
    matched_recipes = [recipe for recipe in recipes if query in recipe['name'].lower()]

    if matched_recipes:
        response = "Найдены рецепты:\n" + "\n".join(f"- {recipe['name']}" for recipe in matched_recipes)
    else:
        response = "Рецепты не найдены. Попробуйте другое название."

    await update.message.reply_text(response)

# Подробности о рецепте
async def recipe_detail(update: Update, context: ContextTypes.DEFAULT_TYPE):
    recipes = await load_recipes()
    query = update.message.text.lower()
    matched_recipes = [recipe for recipe in recipes if query in recipe['name'].lower()]

    if matched_recipes:
        response = "\n\n".join(f"*{recipe['name']}*\n{recipe['preparation']}" for recipe in matched_recipes)
    else:
        response = "Рецепт не найден."

    await update.message.reply_text(response, parse_mode='Markdown')

if __name__ == "__main__":
    app = ApplicationBuilder().token('6953692387:AAEm-p8VtfqdmkHtbs8hxZWS-XNkdRN2lRE').build()
    
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, search_recipes))
    app.add_handler(MessageHandler(filters.TEXT & filters.COMMAND, recipe_detail))

    app.run_polling()
