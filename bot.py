import logging
import nest_asyncio
from telegram import Update, ForceReply
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes, MessageHandler, filters
import json
import httpx

nest_asyncio.apply()
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

# Load recipes from JSON
def load_recipes():
    with open('recipes.json', 'r', encoding='utf-8') as file:
        return json.load(file)

recipes = load_recipes()

# Start command
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    welcome_text = (
        f"👋 Привет, {user.mention_html()}! Добро пожаловать в CheffBot!\n\n"
        "📝 Используйте команду /help, чтобы получить список доступных команд.\n\n"
        "🔍 Введите название рецепта, чтобы найти его."
    )
    await update.message.reply_html(welcome_text)

# Help command
async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    help_text = (
        "🛠 Доступные команды:\n"
        "/start - Запустить бота\n"
        "/help - Помощь\n"
        "/search - Найти рецепт по названию\n"
        "/menu - Показать меню рецептов\n"
        "Введите название рецепта для поиска."
    )
    await update.message.reply_text(help_text)

# Search recipe
async def search_recipe(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.message.text
    found_recipes = [recipe for recipe in recipes if query.lower() in recipe['name'].lower()]
    
    if found_recipes:
        response_text = "🍽️ Найденные рецепты:\n"
        for recipe in found_recipes:
            response_text += f"✅ {recipe['name']} - {recipe['description']}\n"
        await update.message.reply_text(response_text)
    else:
        await update.message.reply_text("❌ Рецепт не найден. Попробуйте другое название.")

# Menu command
async def menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    menu_text = "📋 Меню рецептов:\n"
    for recipe in recipes:
        menu_text += f"📌 {recipe['name']}\n"
    await update.message.reply_text(menu_text)

# Main function to run the bot
async def main():
    app = ApplicationBuilder().token('6953692387:AAEm-p8VtfqdmkHtbs8hxZWS-XNkdRN2lRE').build()
    
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("menu", menu))
    app.add_handler(MessageHandler(filters.text & ~filters.command, search_recipe))
    
    await app.run_polling()

if __name__ == '__main__':
    import asyncio
    asyncio.run(main())
