from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters, CallbackContext
import logging

# Set up logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

# Dummy recipes for demonstration
recipes = {
    'Солянка': {
        'ingredients': {
            'Мясо': '300 г',
            'Картошка': '2 шт',
            'Морковь': '1 шт',
            'Лук': '1 шт',
            'Томатная паста': '2 ст. ложки'
        },
        'instructions': [
            '1. Нарежьте мясо и обжарьте его.',
            '2. Нарежьте картошку, морковь, лук и добавьте в кастрюлю.',
            '3. Добавьте томатную пасту и воду, доведите до кипения.',
            '4. Варите до готовности овощей.',
            '5. Посолите и поперчите по вкусу.'
        ]
    },
    'Борщ': {
        'ingredients': {
            'Свекла': '2 шт',
            'Морковь': '1 шт',
            'Капуста': '300 г',
            'Картошка': '3 шт',
            'Мясо': '400 г',
            'Томатная паста': '2 ст. ложки'
        },
        'instructions': [
            '1. Варите мясо до готовности.',
            '2. Нарежьте свеклу и морковь, обжарьте их.',
            '3. Нарежьте капусту и картошку, добавьте в бульон.',
            '4. Добавьте обжаренные овощи и томатную пасту.',
            '5. Варите до готовности.'
        ]
    }
}

def start(update: Update, context: CallbackContext) -> None:
    update.message.reply_text('Введите название рецепта или ингредиент для поиска:')

def search_recipe(update: Update, context: CallbackContext) -> None:
    query = update.message.text
    matching_recipes = [r for r in recipes if query.lower() in r.lower()]
    
    if not matching_recipes:
        update.message.reply_text('Ничего не найдено. Попробуйте снова.')
        return

    keyboard = []
    for recipe in matching_recipes[:5]:
        button_text = f'{recipe} 🍲'  # Adding an emoji
        keyboard.append([InlineKeyboardButton(button_text, callback_data=f'recipe_{recipe}')])
    
    if len(matching_recipes) > 5:
        keyboard.append([InlineKeyboardButton('Еще', callback_data='more_recipes')])

    update.message.reply_text('Выберите рецепт:', reply_markup=InlineKeyboardMarkup(keyboard))

def handle_query(update: Update, context: CallbackContext) -> None:
    query = update.callback_query
    query.answer()
    data = query.data

    if data.startswith('recipe_'):
        recipe_name = data.replace('recipe_', '')
        recipe = recipes.get(recipe_name)

        if recipe:
            ingredients = '\n'.join([f'- {ing}: {qty}' for ing, qty in recipe['ingredients'].items()])
            instructions = '\n'.join(recipe['instructions'])
            
            recipe_message = f'Ингредиенты:\n{ingredients}\n\nПриготовление:\n{instructions}'
            query.edit_message_text(recipe_message)

            # Sending a new search prompt and removing previous messages
            query.message.reply_text('Введите название рецепта или ингредиент для поиска:')
            context.bot.delete_message(chat_id=query.message.chat_id, message_id=query.message.message_id)
        else:
            query.edit_message_text('Рецепт не найден.')

    elif data == 'more_recipes':
        # Handle loading more recipes (you'll need to implement this part based on your own requirements)
        pass

def main() -> None:
    application = Application.builder().token('6953692387:AAEm-p8VtfqdmkHtbs8hxZWS-XNkdRN2lRE').build()
    
    application.add_handler(CommandHandler('start', start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, search_recipe))
    application.add_handler(CallbackQueryHandler(handle_query))
    
    application.run_polling()

if __name__ == '__main__':
    main()
