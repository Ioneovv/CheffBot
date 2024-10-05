import json
import logging
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
import nest_asyncio
import asyncio

# Включаем nest_asyncio, чтобы избежать конфликта с циклом событий
nest_asyncio.apply()

# Настройка логирования
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

# Загружаем рецепты из JSON файла
def load_recipes(filename):
    try:
        with open(filename, 'r', encoding='utf-8') as file:
            recipes = json.load(file)
            return recipes
    except Exception as e:
        logger.error(f"Ошибка при чтении {filename}: {e}")
        return []

# Команда /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Добро пожаловать в Кулинарного Бота! Используйте /recipe, чтобы получить рецепт.")

# Команда /recipe
async def recipe(update: Update, context: ContextTypes.DEFAULT_TYPE):
    recipes = load_recipes("recipes_part1.json")
    if not recipes:
        await update.message.reply_text("Не удалось загрузить рецепты.")
        return
    
    # Отправляем список рецептов
    message = "Доступные рецепты:\n\n"
    for index, recipe in enumerate(recipes):
        message += f"{index + 1}. {recipe['title']}\n"
    await update.message.reply_text(message)

# Главная функция
async def main():
    application = ApplicationBuilder().token('6953692387:AAEm-p8VtfqdmkHtbs8hxZWS-XNkdRN2lRE').build()
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("recipe", recipe))
    
    print("Бот запущен...")
    await application.run_polling()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except RuntimeError as e:
        if "This event loo
