import asyncio
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters

# Примерный список рецептов
recipes = {
    "Cheesecake": ["cheese", "sugar", "eggs"],
    "Pancakes": ["flour", "milk", "eggs"],
    "Salad": ["lettuce", "tomatoes", "cucumber"]
}

async def start(update: Update, context):
    keyboard = [
        [InlineKeyboardButton("Поиск по названию", callback_data='search_by_name')],
        [InlineKeyboardButton("Поиск по ингредиентам", callback_data='search_by_ingredient')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("Выберите опцию поиска:", reply_markup=reply_markup)

async def button_handler(update: Update, context):
    query = update.callback_query
    await query.answer()

    if query.data == 'search_by_name':
        await query.edit_message_text("Введите название рецепта:")
        context.user_data['search_type'] = 'name'
    elif query.data == 'search_by_ingredient':
        await query.edit_message_text("Введите ингредиент:")
        context.user_data['search_type'] = 'ingredient'

async def handle_message(update: Update, context):
    search_type = context.user_data.get('search_type')
    query = update.message.text.lower()

    if search_type == 'name':
        results = [name for name in recipes if query in name.lower()]
    elif search_type == 'ingredient':
        results = [name for name, ingredients in recipes.items() if query in (ingredient.lower() for ingredient in ingredients)]
    else:
        results = []

    if results:
        await update.message.reply_text(f"Найдены рецепты: {', '.join(results)}")
    else:
        await update.message.reply_text("Ничего не найдено.")

async def main():
    application = Application.builder().token("YOUR_TOKEN").build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CallbackQueryHandler(button_handler))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    await application.start()
    await application.idle()

if __name__ == '__main__':
    asyncio.run(main())
