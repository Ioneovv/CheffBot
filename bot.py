import json
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

# Функция для загрузки рецептов из файлов
def load_recipes():
    recipes = []
    for filename in ["recipes_part1.json", "recipes_part2.json"]:
        try:
            with open(filename, "r", encoding="utf-8") as file:
                data = json.load(file)
                recipes.extend(data)
                print(f"Файл {filename} загружен успешно!")
        except FileNotFoundError:
            print(f"Ошибка: файл {filename} не найден.")
        except json.JSONDecodeError as e:
            print(f"Ошибка при чтении {filename}: {e}")
    return recipes

# Функция для обработки команды /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Привет! Я бот для рецептов. Используйте команду /recipe для получения рецепта.")

# Функция для обработки команды /recipe
async def recipe(update: Update, context: ContextTypes.DEFAULT_TYPE):
    recipes = load_recipes()
    if recipes:
        # Просто отправим первый рецепт для примера
        recipe = recipes[0]
        response = f"**{recipe['title']}**\n*Категория:* {recipe['category']}\n\n**Ингредиенты:**\n"
        for ingredient in recipe['ingredients']:
            response += f"- {ingredient['ingredient']}: {ingredient['amount']}\n"
        response += "\n**Инструкция:**\n"
        for step in recipe['instructions']:
            response += f"- {step}\n"
        await update.message.reply_text(response, parse_mode='Markdown')
    else:
        await update.message.reply_text("Извините, рецепты не найдены.")

# Главная функция
async def main():
    application = ApplicationBuilder().token('6953692387:AAEm-p8VtfqdmkHtbs8hxZWS-XNkdRN2lRE').build()
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("recipe", recipe))
    
    print("Бот запущен...")
    await application.run_polling()

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
