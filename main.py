from telegram import Update, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes, ConversationHandler
from dotenv import load_dotenv
import os
from model import generate_recipe  # Імпортуємо наш обробник
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import ContextTypes
from telegram.ext import Application, CallbackQueryHandler
from func import *

# Завантажуємо API_TOKEN з .env файла
load_dotenv()
api_token = os.getenv('API_TOKEN')

# Стан для ConversationHandler
LANGUAGE, MENU, INGREDIENTS, CONFIRM_INGREDIENTS, SELECT_CUISINE, CONFIRM_RECIPE, SETTINGS = range(7)

# Мови інтерфейсу
language_data = {
    "Ukrainian 🇺🇦": {
        "cuisine": "Кухня",
        "ingredients": "Інгредієнти",
        "recipe_generated": "🎉🍽️ Ваш рецепт створено!",
        "error_message": "😞 Ой, сталася помилка!",
        "language_selected": "🇺🇦 Ви обрали українську мову!",
        "menu": ["🍳 Створити рецепт", "⚙️ Налаштування"],
        "ask_ingredients": "🥕🍅 Будь ласка, надайте список продуктів:",
        "confirm_ingredients": "✅/❌ Це всі інгредієнти?",
        "ask_cuisine": "🌍🍴 У якому стилі кухні ви бажаєте рецепт?",
        "confirmation_message": "🤔🍽️ Перевірте інформацію. Генеруємо рецепт?",
        "cancel": "Відмінити ❌",
        "back": "⬅️ Назад",
        "yes": "Так ✅",
        "no": "Ні ❌",
        "recipe_generating": "⏳Ми готуємо ваш рецепт... 🍳 Будь ласка, трохи зачекайте! 😊",
        "recipe_generated": "🎉 Ваш рецепт готовий! 🍽️ Що ви хочете зробити далі? 😊",
        "next_page": "➡️",
        "back_page": "⬅️",
        "main_menu": "🌟 Ви знову на головній сторінці!",
        "settings": {
            "menu_message": "⚙️ Меню налаштувань:\nОберіть опцію:",
            "change_language": "🌍 Змінити мову",
            "about_author": "ℹ️ Про автора",
            "author_info": "👨‍💻 Автор: Микита Гончаренко\n",
            "link_git": "https://github.com/Nikitatoser",
            "link_In": "https://www.linkedin.com/in/mykyta-honcharenkko/",
        },
        "language_select_message": "🌍 Будь ласка, оберіть мову:",
    },
    "English 🇺🇸": {
        "cuisine": "Cuisine",
        "ingredients": "Ingredients",
        "recipe_generated": "🎉🍽️ Your recipe has been generated!",
        "error_message": "😞 Oops, something went wrong!",
        "language_selected": "🇺🇸 You have selected English!",
        "menu": ["🍳 Create Recipe", "⚙️ Settings"],
        "ask_ingredients": "🥕🍅 Please provide the list of ingredients:",
        "confirm_ingredients": "✅/❌ Is this all the ingredients?",
        "ask_cuisine": "🌍🍴 What cuisine style would you like?",
        "confirmation_message": "🤔🍽️ Check the information. Ready to generate the recipe?",
        "cancel": "Cancel ❌",
        "back": "⬅️ Back",
        "yes": "Yes ✅",
        "no": "No ❌",
        "recipe_generating": "⏳ We're cooking up your recipe... 🍳 Please wait a moment! 😊",
        "recipe_generated": "🎉 Your recipe is ready! 🍽️ What would you like to do next? 😊",
        "next_page": "➡️",
        "back_page": "⬅️",
        "main_menu": "🌟 You are back on the main page!",
        "settings": {
            "menu_message": "⚙️ Settings Menu:\nChoose an option:",
            "change_language": "🌍 Change Language",
            "about_author": "ℹ️ About Author",
            "author_info": "👨‍💻 Author: Mykyta Honcharenko\n",
            "link_git": "https://github.com/Nikitatoser",
            "link_In": "https://www.linkedin.com/in/mykyta-honcharenkko/",
        },
        "language_select_message": "🌍 Please select your language:",
    },
    "German 🇩🇪": {
        "cuisine": "Küche",
        "ingredients": "Zutaten",
        "recipe_generated": "🎉🍽️ Ihr Rezept wurde erstellt!",
        "error_message": "😞 Ups, etwas ist schief gelaufen!",
        "language_selected": "🇩🇪 Sie haben Deutsch ausgewählt!",
        "menu": ["🍳 Rezept erstellen", "⚙️ Einstellungen"],
        "ask_ingredients": "🥕🍅 Bitte geben Sie die Zutatenliste an:",
        "confirm_ingredients": "✅/❌ Sind das alle Zutaten?",
        "ask_cuisine": "🌍🍴 Welche Küchenrichtung möchten Sie?",
        "confirmation_message": "🤔🍽️ Überprüfen Sie die Informationen. Möchten Sie das Rezept generieren?",
        "cancel": "Abbrechen ❌",
        "back": "⬅️ Zurück",
        "yes": "Ja ✅",
        "no": "Nein ❌",
        "recipe_generating": "⏳ Wir zaubern dein Rezept... 🍳 Bitte warte einen Moment! 😊",
        "recipe_generated": "🎉 Dein Rezept ist fertig! 🍽️ Was möchtest du als Nächstes tun? 😊",
        "next_page": "➡️",
        "back_page": "⬅️",
        "main_menu": "🌟 Sie sind wieder auf der Hauptseite!",
        "settings": {
            "menu_message": "⚙️ Einstellungsmenü:\nWählen Sie eine Option:",
            "change_language": "🌍 Sprache ändern",
            "about_author": "ℹ️ Über den Autor",
            "author_info": "👨‍💻 Autor: Mykyta Honcharenko\n",
            "link_git": "https://github.com/Nikitatoser",
            "link_In": "https://www.linkedin.com/in/mykyta-honcharenkko/",
        },
        "language_select_message": "🌍 Bitte wählen Sie Ihre Sprache:",
    },
}

# Словник для мови
user_language = {}

# Головна функція
def main():
    application = Application.builder().token(api_token).build()
    
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            LANGUAGE: [MessageHandler(filters.TEXT & ~filters.COMMAND, set_language)],
            MENU: [MessageHandler(filters.TEXT & ~filters.COMMAND, menu)],
            INGREDIENTS: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_ingredients)],
            CONFIRM_INGREDIENTS: [MessageHandler(filters.TEXT & ~filters.COMMAND, confirm_ingredients)],
            SELECT_CUISINE: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, handle_cuisine_selection),
                CallbackQueryHandler(handle_cuisine_selection)  # Обработка инлайн-кнопок
            ],
            CONFIRM_RECIPE: [MessageHandler(filters.TEXT & ~filters.COMMAND, confirm_recipe)],
            SETTINGS: [MessageHandler(filters.TEXT & ~filters.COMMAND, settings)],
        },
        fallbacks=[MessageHandler(filters.TEXT & ~filters.COMMAND, cancel)],
    )
    
    # Добавляем ConversationHandler в приложение
    application.add_handler(conv_handler)

    # Запуск бота
    application.run_polling()

if __name__ == '__main__':
    main()
