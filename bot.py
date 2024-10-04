import json
import logging
import os
from telegram import Update, ForceReply
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes

# Настройки логирования
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

# Загрузка рецептов из файла
def load_recipes():
    try:
        with open('recipes.json', 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        logger.error(f"Ошибка загрузки или обработки recipes.json: {e}")
        return []

# Обработчик команды /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user = update.effective_user
    await update.message.reply_html(
        rf"Привет, {user.mention_html()}! Я бот с рецептами. Напиши 'поиск' для поиска рецептов.",
        reply_markup=ForceReply(selective=True),
    )

# Обработчик команды /help
async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text("Команды:\n/start - начать общение\n/help - помощь\n/поиск - поиск рецептов")

# Обработчик поиска рецептов
async def search_recipes(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    recipes = load_recipes()
    if not recipes:
        await update.message.reply_text("Нет доступных рецептов.")
        return
    
    query = update.message.text
    results = [recipe for recipe in recipes if query.lower() in recipe['name'].lower()]

    if results:
        response = "\n".join([f"{i+1}. {recipe['name']}" for i, recipe in enumerate(results)])
        await update.message.reply_text(f"Результаты поиска:\n{response}")
    else:
        await update.message.reply_text("Рецепты не найдены.")

# Обработчик выбора рецепта
async def recipe_detail(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    recipes = load_recipes()
    try:
        recipe_index = int(update.message.text) - 1
        recipe = recipes[recipe_index]
        await update.message.reply_text(f"Рецепт: {recipe['name']}\n\nПриготовление:\n{recipe['instructions']}")
    except (IndexError, ValueError):
        await update.message.reply_text("Неправильный номер рецепта.")

# Основная функция
async def main() -> None:
    app = ApplicationBuilder().token('6953692387:AAEm-p8VtfqdmkHtbs8hxZWS-XNkdRN2lRE').build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, search_recipes))
    app.add_handler(MessageHandler(filters.TEXT & filters.COMMAND, recipe_detail))

    await app.run_polling()

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
