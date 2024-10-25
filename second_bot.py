from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
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

# Функція для обробки помилок
async def error_handler(update, context):
    logging.error(f"Виникла помилка: {context.error}")

# Старт бота і кнопка 'Зареєструватися'
async def start(update: Update, context):
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
    context.user_data["full_name"] = update.message.text.strip()
    await update.message.reply_text("Введіть свій номер телефону:")
    return PHONE #повертаємо наступний стан розмови


# Зберігаємо номер в контекст розмови та запитуємо пошту
async def phone(update: Update, context: ContextTypes.DEFAULT_TYPE):   
    context.user_data["phone_number"] = update.message.text.strip()
    await update.message.reply_text("Введіть свою пошту:")
    return EMAIL
    

#Скасування реєстрації і кінець розмови
async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    await update.message.reply_text("Реєстрацію скасовано!")
    return ConversationHandler.END


# Основна частина програми
if __name__ == '__main__':
    application = ApplicationBuilder().token('ДОДАЙ СВІЙ ТОКЕН ТУТ').build()
    application.add_error_handler(error_handler)

    # Додаємо обробник для команди /start
    application.add_handler(CommandHandler('start', start))

    conv_handler = ConversationHandler(
        entry_points=[CallbackQueryHandler(registration, pattern='^registration$')], #початок реєстрації (після натискання на кнопку "Зареєструватися")
        states={
            FULL_NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, full_name)], # перше запитання
            PHONE: [MessageHandler(filters.TEXT & ~filters.COMMAND, phone)], # друге запитаня
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )

    application.add_handler(conv_handler)

    # Запускаємо бота
    application.run_polling()
