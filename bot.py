import asyncio
import requests
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters, CallbackContext

# Прямая ссылка на JSON-файл на Google Drive
RECIPE_URL = "https://drive.google.com/uc?export=download&id=16j85IZTSaOLBD5AqHWJ5mux50jXZ6UxT"

def load_recipes():
    try:
        response = requests.get(RECIPE_URL)
        response.raise_for_status()
        return response.json().get('recipes', [])
    except requests.RequestException as e:
        print(f"Failed to load recipes: {e}")
        return []

recipes = load_recipes()

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

async def start(update: Update, context: CallbackContext):
    categories = get_categories()
    keyboard = [[InlineKeyboardButton(f"🍽 {category}", callback_data=f'category_{category}')] for category in categories]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text('Выберите категорию рецептов:', reply_markup=reply_markup)

async def category_button(update: Update, context: CallbackContext):
    query = update.callback_query
    await query.answer()
    category = query.data.split('_')[1]

    recipes_in_category = [recipe for recipe in recipes if recipe['category'] == category]

    if not recipes_in_category:
        await query.message.reply_text("Нет рецептов в этой категории.")
        return

    keyboard = [[InlineKeyboardButton(f"🍽 {recipe['title']}", callback_data=f'recipe_{category}_{i}')] for i, recipe in enumerate(recipes_in_category)]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.message.edit_text("Выберите рецепт:", reply_markup=reply_markup)

async def recipe_button(update: Update, context: CallbackContext):
    query = update.callback_query
    await query.answer()

    try:
        data = query.data.split('_')
        category = data[1]
        recipe_index = int(data[2])
        recipes_in_category = [recipe for recipe in recipes if recipe['category'] == category]
        
        if 0 <= recipe_index < len(recipes_in_category):
            recipe = recipes_in_category[recipe_index]
            recipe_text = format_recipe(recipe)

            await query.message.delete()
            await query.message.reply_text(recipe_text, parse_mode='Markdown')

            # Отправляем кнопки для выбора категории
            keyboard = [[InlineKeyboardButton(f"🍽 {cat}", callback_data=f'category_{cat}')] for cat in get_categories()]
            reply_markup = InlineKeyboardMarkup(keyboard)
            await query.message.reply_text("Выберите категорию рецептов:", reply_markup=reply_markup)
        else:
            await query.message.reply_text("Ошибка: Рецепт не найден.")
    except Exception as e:
        print(f"Error in recipe_button handler: {e}")
        await query.message.reply_text("Произошла ошибка. Попробуйте снова.")

async def main():
    application = Application.builder().token("6953692387:AAEm-p8VtfqdmkHtbs8hxZWS-XNkdRN2lRE").build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CallbackQueryHandler(category_button, pattern='^category_'))
    application.add_handler(CallbackQueryHandler(recipe_button, pattern='^recipe_'))

    await application.initialize()
    await application.start()
    await application.updater.start_polling()
    await asyncio.Event().wait()

if __name__ == '__main__':
    asyncio.run(main())
