import asyncio
import requests
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters, CallbackContext

# Загрузите JSON-файл с рецептами
RECIPE_URL = "https://drive.google.com/uc?export=download&id=1ZJRccW9YjpI0O8Q7eQ8PFCH5WC-6G-Yb"

def load_recipes():
    response = requests.get(RECIPE_URL)
    response.raise_for_status()
    return response.json()

recipes = load_recipes()

def search_recipes(query):
    results = []
    for recipe in recipes:
        title = recipe.get('title', '').lower()
        ingredients = [ing['ingredient'].lower() for ing in recipe.get('ingredients', [])]
        if query.lower() in title or any(query.lower() in ing for ing in ingredients):
            results.append(recipe)
    return results

def format_recipe(recipe):
    recipe_text = f"🍽 **{recipe['title']}**\n\n"
    recipe_text += "📝 **Ингредиенты:**\n"
    for ingredient in recipe.get('ingredients', []):
        amount = ingredient.get('amount', '')
        recipe_text += f"- {ingredient['ingredient']} ({amount})\n"
    recipe_text += "\n🧑‍🍳 **Приготовление:**\n"
    for i, step in enumerate(recipe.get('instructions', []), start=1):
        recipe_text += f"{i}. {step}\n"
    return recipe_text

async def start(update: Update, context: CallbackContext):
    keyboard = [
        [InlineKeyboardButton("🔍 Поиск по названию", callback_data='search_by_title')],
        [InlineKeyboardButton("🍴 Поиск по ингредиентам", callback_data='search_by_ingredients')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text('Выберите способ поиска рецепта:', reply_markup=reply_markup)

async def button(update: Update, context: CallbackContext):
    query = update.callback_query
    await query.answer()

    try:
        if query.data.startswith('recipe_'):
            recipe_index = int(query.data.split('_')[1])
            recipe = context.user_data.get('current_results', [])[recipe_index]
            recipe_text = format_recipe(recipe)

            await query.message.delete()

            await query.message.reply_text(recipe_text, parse_mode='Markdown')

            keyboard = [
                [InlineKeyboardButton("🔍 Поиск по названию", callback_data='search_by_title')],
                [InlineKeyboardButton("🍴 Поиск по ингредиентам", callback_data='search_by_ingredients')]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            await update.message.reply_text("Выберите способ поиска рецепта:", reply_markup=reply_markup)

        elif query.data in ['search_by_title', 'search_by_ingredients']:
            await query.edit_message_text(text="Введите название рецепта или ингредиент для поиска:")
            context.user_data['search_type'] = query.data

    except Exception as e:
        print(f"Error: {e}")
        await query.message.reply_text("Произошла ошибка. Попробуйте снова.")

async def handle_message(update: Update, context: CallbackContext):
    query = update.message.text
    search_type = context.user_data.get('search_type')

    if search_type in ['search_by_title', 'search_by_ingredients']:
        results = search_recipes(query)[:5]
        context.user_data['current_results'] = results

        if not results:
            await update.message.reply_text("Ничего не найдено.")
            return

        keyboard = []
        for i, recipe in enumerate(results):
            keyboard.append([InlineKeyboardButton(f"🍽 {recipe['title']}", callback_data=f'recipe_{i}')])

        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.message.reply_text("Выберите рецепт:", reply_markup=reply_markup)

    else:
        await update.message.reply_text("Пожалуйста, выберите способ поиска.")

async def main():
    application = Application.builder().token("6953692387:AAEm-p8VtfqdmkHtbs8hxZWS-XNkdRN2lRE").build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CallbackQueryHandler(button))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    await application.initialize()
    await application.start()
    await application.updater.start_polling()
    await asyncio.Event().wait()

if __name__ == '__main__':
    asyncio.run(main())
