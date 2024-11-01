from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
import sqlite3
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    ContextTypes,
    ConversationHandler,
    MessageHandler,
    filters,
    CallbackQueryHandler
)

import logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

logging.getLogger("httpx").setLevel(logging.WARNING)

logger = logging.getLogger(__name__)
# стани (етапи) розмови 
FULL_NAME, PHONE, EMAIL, AGE, CITY = 0, 1, 2, 3, 4
ADMIN_ID = 0 # ТУТ ДОДАТИ АЙДІ АДМІНА

# Функція для обробки помилок
async def error_handler(update, context):
    logging.error(f"Виникл  а помилка: {context.error}")


def checking_user(tg_id):
    connection = sqlite3.connect("tg_bot.db")
    cursor = connection.cursor()
    cursor.execute('''SELECT  * FROM applications 
                   WHERE telegram_id = ? ''',[tg_id])
    info_user = cursor.fetchone()
    connection.close()
    return info_user


def add_to_db(data):
    connection = sqlite3.connect("tg_bot.db")
    cursor = connection.cursor()
    cursor.execute('''INSERT INTO applications(full_name, phone_number, email, age , city, telegram_id)
                   VALUES (?,?,?,?,?,?) 
                   ''', [data["full_name"], data['phone_number'],data["email"],data["age"],data["city"],data["tg_id"]])
    connection.commit()
    connection.close()

# Старт бота і кнопка 'Зареєструватися'
async def start(update: Update, context):
    if checking_user(update.message.from_user.id):
        await  update.message.reply_text("Ви вже зареєстровані!")
    else:    
        keyboard = [[InlineKeyboardButton("Зареєструватися", callback_data='registration')]]
        reply_markup = InlineKeyboardMarkup(keyboard)

        await update.message.reply_text("Вітаю, вас було запрошено на подію!", reply_markup=reply_markup)

# Початок реєстрації
async def registration(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()  # Якщо користувач натиснув на кнопку "Зареєструватися"
    await query.message.reply_text("Введіть своє повне ім'я:") # запитуємо ім'я

    return FULL_NAME #повертаємо наступний стан розмови


# Зберігаємо ім'я в контекст розмови та запитуємо номер телефону
async def full_name(update: Update, context: ContextTypes.DEFAULT_TYPE):  
    name = update.message.text.strip().capitalize()
    if not name.isalpha():
        await update.message.reply_text("Імя повинно бути з літер!:")
        return FULL_NAME
    
    context.user_data["full_name"] = name
    await update.message.reply_text("Введіть свій номер телефону:")
    return PHONE #повертаємо наступний стан розмови


# Зберігаємо номер в контекст розмови та запитуємо пошту


async def phone(update: Update, context: ContextTypes.DEFAULT_TYPE):   
    phone = update.message.text.strip()
    if (not phone.isnumeric()) or len(phone) < 10 :
        await update.message.reply_text("Номер має складатись  не менше ніж 10  чисел!")
        return PHONE

    context.user_data["phone_number"] = update.message.text.strip()
    await update.message.reply_text("Введіть свою пошту:")
    return EMAIL
    
async def email(update: Update, context: ContextTypes.DEFAULT_TYPE):   
    context.user_data["email"] = update.message.text.strip()
    await update.message.reply_text("Введіть свій вік:")
    return AGE

async def age(update: Update, context: ContextTypes.DEFAULT_TYPE):   
    context.user_data["age"] = update.message.text.strip()
    await update.message.reply_text("Введіть своє місто:")
    return CITY


async def city(update: Update, context: ContextTypes.DEFAULT_TYPE):   
    context.user_data["city"] = update.message.text.strip()
    context.user_data["tg_id"] = update.message.from_user.id
    add_to_db(context.user_data)
    await update.message.reply_text(" Реєстрацію завершено!")
    logger.info(f"Збережено анкету{ context.user_data}")
    text = f'''Зареєстровано нового користувача з даними:
Ім'я: {context.user_data['full_name']}
Номер: {context.user_data['phone_number']}
Email:{context.user_data['email']}
Вік: {context.user_data['age']}
Місто: {context.user_data['city']}
ID: {context.user_data['tg_id']}'''
    await context.bot.send_message(chat_id = ADMIN_ID, text = text  )
    
    return ConversationHandler.END



#Скасування реєстрації і кінець розмови
async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    await update.message.reply_text("Реєстрацію скасовано!")
    return ConversationHandler.END


# Основна частина програми
if __name__ == '__main__':
    application = ApplicationBuilder().token('TOKEN').build()
    application.add_error_handler(error_handler)

    # Додаємо обробник для команди /start
    application.add_handler(CommandHandler('start', start))

    conv_handler = ConversationHandler(
        entry_points=[CallbackQueryHandler(registration, pattern='^registration$')], #початок реєстрації (після натискання на кнопку "Зареєструватися")
        states={
            
            FULL_NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, full_name)], # перше запитання
            PHONE: [MessageHandler(filters.TEXT & ~filters.COMMAND, phone)], # друге запитаня
            EMAIL: [MessageHandler(filters.TEXT & ~filters.COMMAND, email)],
            AGE: [MessageHandler(filters.TEXT & ~filters.COMMAND, age)],
            CITY: [MessageHandler(filters.TEXT & ~filters.COMMAND,city )],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )

    application.add_handler(conv_handler)

    # Запускаємо бота
    application.run_polling()
