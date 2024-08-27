from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Updater, CommandHandler, CallbackQueryHandler, CallbackContext
import json

# Загрузите рецепты из файла
with open('recipes.json', 'r', encoding='utf-8') as f:
    recipes = json.load(f)

def start(update: Update, context: CallbackContext):
    keyboard = [
        [InlineKeyboardButton("Поиск рецепта", callback_data='search')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    update.message.reply_text('Привет! Нажмите кнопку ниже, чтобы начать поиск рецептов.', reply_markup=reply_markup)

def button(update: Update, context: CallbackContext):
    query = update.callback_query
    query.answer()

    if query.data == 'search':
        query.edit_message_text(text="Введите ингредиенты для поиска (через запятую):")

        # Установите состояние ожидания ингредиентов
        context.user_data['waiting_for_ingredients'] = True

def handle_message(update: Update, context: CallbackContext):
    if context.user_data.get('waiting_for_ingredients'):
        ingredients = update.message.text.strip().split(',')
        ingredients = [ing.strip().lower() for ing in ingredients]

        # Поиск рецептов
        matching_recipes = []
        for recipe in recipes:
            if all(ingredient in recipe['ingredients'] for ingredient in ingredients):
                matching_recipes.append(f"Название: {recipe['title']}\nИнструкция: {recipe['instructions']}")

        if matching_recipes:
            update.message.reply_text('\n\n'.join(matching_recipes))
        else:
            update.message.reply_text("Рецепты с такими ингредиентами не найдены.")

        # Сброс состояния ожидания
        context.user_data['waiting_for_ingredients'] = False

def main():
    updater = Updater("YOUR_TELEGRAM_BOT_TOKEN", use_context=True)

    dp = updater.dispatcher
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CallbackQueryHandler(button))
    dp.add_handler(MessageHandler(Filters.text & ~Filters.command, handle_message))

    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()

