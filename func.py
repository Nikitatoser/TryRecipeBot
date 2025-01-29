from telegram import Update, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes, ConversationHandler
from dotenv import load_dotenv
import os
from model import generate_recipe  # Імпортуємо наш обробник
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import ContextTypes
from telegram.ext import Application, CallbackQueryHandler
from main import *

# Функція для обробки команди /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    # Привітальне повідомлення з описом бота
    greeting_message = (
        "👋 Welcome to TryRecipeBot! 🤖\n\n"
        "🔸I'm here to help you create amazing recipes based on the ingredients you have! 🌱🍅\n"
        "🔹Just provide me with a list of ingredients, choose a cuisine style, and I'll generate a delicious recipe for you! 🍽️🎉\n\n"
        "🌍 Please select your language to get started:"
    )
    
    # Кнопки для вибору мови
    kb = [[KeyboardButton(lang)] for lang in language_data.keys()]
    keyboard = ReplyKeyboardMarkup(kb, resize_keyboard=True)
    
    # Відправка повідомлення з привітанням і вибором мови
    await update.message.reply_text(greeting_message, reply_markup=keyboard)
    
    return LANGUAGE


# Обробка вибору мови
async def set_language(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    language = update.message.text
    if language in language_data:
        user_language[update.message.chat_id] = language
        data = language_data[language]
        kb = [[KeyboardButton(option)] for option in data["menu"]]
        keyboard = ReplyKeyboardMarkup(kb, resize_keyboard=True)
        await update.message.reply_text(data["language_selected"], reply_markup=keyboard)
        return MENU
    else:
        await update.message.reply_text("❌ Oops! That language is not available. Please choose again. 🌍🙂")
        return LANGUAGE

# Функція для обробки меню
async def menu(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    language = user_language[update.message.chat_id]
    data = language_data[language]
    if update.message.text == data["menu"][0]:  # "Create Recipe"
        kb = [[KeyboardButton(data["cancel"])]]
        keyboard = ReplyKeyboardMarkup(kb, resize_keyboard=True)
        await update.message.reply_text(data["ask_ingredients"], reply_markup=keyboard)
        return INGREDIENTS
    elif update.message.text == data["menu"][1]:  # "Settings"
        # Добавляем подменю настроек
        kb = [
            [KeyboardButton(data["settings"]["change_language"])],
            [KeyboardButton(data["settings"]["about_author"])],
            [KeyboardButton(data["back"])],
        ]
        keyboard = ReplyKeyboardMarkup(kb, resize_keyboard=True)
        await update.message.reply_text(data["settings"]["menu_message"], reply_markup=keyboard)
        return SETTINGS
    else:
        await update.message.reply_text("Please choose a valid option.")
        return MENU


# Функция для обработки настроек
async def settings(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    language = user_language[update.message.chat_id]
    data = language_data[language]
    if update.message.text == data["settings"]["change_language"]:  # "Change Language"
        # Перенаправляем на выбор языка
        kb = [[KeyboardButton(lang)] for lang in language_data.keys()]
        keyboard = ReplyKeyboardMarkup(kb, resize_keyboard=True)
        await update.message.reply_text(data["language_select_message"], reply_markup=keyboard)
        return LANGUAGE
    elif update.message.text == data["settings"]["about_author"]:  # "About Author"
        # Створюємо inline-кнопку з посиланням
        keyboard = [
            [InlineKeyboardButton("GitHub", url=data["settings"]["link_git"])],
            [InlineKeyboardButton("LinkedIn", url=data["settings"]["link_In"])],
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        # Відправляємо текст про автора та кнопку з посиланням
        await update.message.reply_text(data["settings"]["author_info"], reply_markup=reply_markup)
        return SETTINGS
    elif update.message.text == data["back"]:  # "Back to Menu"
        # Возвращаем пользователя в главное меню
        kb = [[KeyboardButton(option)] for option in data["menu"]]
        keyboard = ReplyKeyboardMarkup(kb, resize_keyboard=True)
        await update.message.reply_text(data["main_menu"], reply_markup=keyboard)
        return MENU
    else:
        await update.message.reply_text("Please choose a valid option.")
        return SETTINGS


# Обробка списку продуктів
async def get_ingredients(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    if update.message.text.lower() == language_data[user_language[update.message.chat_id]]["cancel"].lower():
        return await cancel(update, context)

    context.user_data["ingredients"] = update.message.text.split(",")
    language = user_language[update.message.chat_id]
    data = language_data[language]
    kb = [[KeyboardButton(data["yes"]), KeyboardButton(data["no"])], [KeyboardButton(data["back"])]]
    keyboard = ReplyKeyboardMarkup(kb, resize_keyboard=True)
    await update.message.reply_text(data["confirm_ingredients"], reply_markup=keyboard)
    return CONFIRM_INGREDIENTS


async def confirm_ingredients(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    language = user_language[update.message.chat_id]
    data = language_data[language]

    if update.message.text == data["yes"]:
    
        return await select_cuisine(update, context)
    elif update.message.text == data["no"] or update.message.text == data["back"]:
        kb = [[KeyboardButton(data["cancel"])]]
        keyboard = ReplyKeyboardMarkup(kb, resize_keyboard=True)
        await update.message.reply_text(data["ask_ingredients"], reply_markup=keyboard)
        return INGREDIENTS
    else:
        await update.message.reply_text(f"❓ {data['invalid_option_message']} Please choose '{data['yes']}', '{data['no']}', or '{data['back']}' to proceed. 😊")
        return 


async def select_cuisine(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    # Определяем, откуда пришёл запрос (сообщение или нажатие кнопки)
    if update.callback_query:
        chat_id = update.callback_query.message.chat_id
    elif update.message:
        chat_id = update.message.chat_id
    else:
        # Если ни message, ни callback_query нет, логируем и выходим
        print("Neither message nor callback_query found in update.")
        return ConversationHandler.END

    # Проверяем на отмену
    if update.message and update.message.text.lower() == language_data[user_language[chat_id]]["cancel"].lower():
        return await cancel(update, context)

    language = user_language[chat_id]
    data = language_data[language]

    cuisines = [
        "Italian 🍝", "Mexican 🌮", "Japanese 🍣", "Indian 🍛", "French 🥖", "Chinese 🍜", 
        "Greek 🥗", "Thai 🍤", "Spanish 🍤", "American 🍔"
    ]


    page_size = 3  # Number of items per page
    pages = [cuisines[i:i + page_size] for i in range(0, len(cuisines), page_size)]

    if "page" not in context.user_data:
        context.user_data["page"] = 0

    current_page = context.user_data["page"]
    page = pages[current_page]


    keyboard = [[InlineKeyboardButton(cuisine, callback_data=cuisine)] for cuisine in page]


    nav_buttons = []
    if current_page > 0:
        nav_buttons.append(InlineKeyboardButton(data["back_page"], callback_data="prev_page"))
    if current_page < len(pages) - 1:
        nav_buttons.append(InlineKeyboardButton(data["next_page"], callback_data="next_page"))
    
    if nav_buttons:
        keyboard.append(nav_buttons)

 
    reply_markup = InlineKeyboardMarkup(keyboard)


    if update.callback_query:
        await update.callback_query.edit_message_text(data["ask_cuisine"], reply_markup=reply_markup)
    else:
        await update.message.reply_text(data["ask_cuisine"], reply_markup=reply_markup)
    
    return SELECT_CUISINE


async def next_page(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data["page"] += 1
    return await select_cuisine(update, context)

async def previous_page(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data["page"] -= 1
    return await select_cuisine(update, context)

async def handle_cuisine_selection(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    query = update.callback_query
    await query.answer()

    if query.data == "next_page":
        return await next_page(update, context)
    elif query.data == "prev_page":
        return await previous_page(update, context)
    else:

        context.user_data["cuisine"] = query.data
        await query.edit_message_text(f"🍽 You selected {query.data}. Now, let's proceed with the recipe!")
        return CONFIRM_RECIPE


async def confirm_recipe(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    language = user_language.get(update.message.chat_id, "English 🇺🇸")
    data = language_data.get(language, language_data["English 🇺🇸"])

    # Отримання даних інгредієнтів та вибраної кухні
    ingredients_list = context.user_data.get("ingredients", [])
    cuisine = context.user_data.get("cuisine", "")

    if not ingredients_list or not cuisine:
        await update.message.reply_text(data["error_message"])
        return MENU

    # Виведення повідомлення для підтвердження
    confirmation_message = (
        f"{data['confirmation_message']}\n\n"
        f"🍴 {data['cuisine']}: {cuisine}\n"
        f"📝 {data['ingredients']}: {', '.join(ingredients_list)}\n\n"
    )
    kb = [
        [KeyboardButton(data["yes"]), KeyboardButton(data["no"])],
    ]
    keyboard = ReplyKeyboardMarkup(kb, resize_keyboard=True)
    await update.message.reply_text(confirmation_message, reply_markup=keyboard)

    # Очікуємо підтвердження або відмову
    if update.message.text == data["yes"]:
        # Користувач підтвердив генерацію рецепту
        await update.message.reply_text(data["recipe_generating"])

        try:
            # Генерація рецепту
            recipe = generate_recipe(", ".join(ingredients_list), cuisine, language)

            # Форматування відповіді
            response = f"{data['recipe_generated']}\n\n<b>{recipe['title']}</b>\n"
            response += "\n".join(f"🔹 {ingredient}" for ingredient in recipe["ingredients"])
            response += "\n\n" + "\n".join(f"{instruction}" for instruction in recipe["instructions"])

            await update.message.reply_text(response, parse_mode="HTML")
        except Exception as e:
            # Обробка помилок
            await update.message.reply_text(f"{data['error_message']}: {str(e)}")

        # Повертаємося до головного меню
        kb = [[KeyboardButton(option)] for option in data["menu"]]
        keyboard = ReplyKeyboardMarkup(kb, resize_keyboard=True)
        await update.message.reply_text(data["recipe_generated"], reply_markup=keyboard)
        return MENU

    elif update.message.text == data["no"]:
        # Користувач хоче змінити дані
        kb = [[KeyboardButton(data["cancel"])]]
        keyboard = ReplyKeyboardMarkup(kb, resize_keyboard=True)
        await update.message.reply_text(data["ask_ingredients"], reply_markup=keyboard)
        return INGREDIENTS

    else:
        # Неправильна відповідь
        await update.message.reply_text(data["invalid_option"])
        return CONFIRM_RECIPE



# Відміна дій
async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    language = user_language[update.message.chat_id]
    data = language_data[language]
    kb = [[KeyboardButton(option)] for option in data["menu"]]
    keyboard = ReplyKeyboardMarkup(kb, resize_keyboard=True)
    await update.message.reply_text("❌ Action canceled. Don't worry, you can try again anytime! 😊", reply_markup=keyboard)
    return MENU
