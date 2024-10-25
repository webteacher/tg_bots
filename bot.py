from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters

# Функція для обробки команди /start
async def start(update: Update, context):
    await update.message.reply_text("Купи слона")

async def hi(update: Update, context):
    await update.message.reply_text("gvgvygvuwubigreeee")

async def echo(update: Update, context):
    await update.message.reply_text(f"Усі так кажуть: {update.message.text}. А ти купи слона!")



# Основна частина програми
if __name__ == '__main__':
    application = ApplicationBuilder().token('ДОДАЙ СВІЙ ТОКЕН ТУТ').build()
    
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, echo))

    # Додаємо обробник для команди /start
    application.add_handler(CommandHandler('start', start))
    application.add_handler(CommandHandler("hi", hi ))

    # Запускаємо бота
    application.run_polling()