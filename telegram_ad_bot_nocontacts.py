import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder, CommandHandler, MessageHandler, filters,
    ConversationHandler, CallbackQueryHandler, ContextTypes
)

BOT_TOKEN = '7588445095:AAFbowVOxKispj00FfKmBKrKRfQxQTKyt44'
ADMIN_CHAT_ID = 672260476  # 

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

(
    CHOOSING_PACKAGE,
    GET_FULLNAME,
    GET_ACTIVITY,
    GET_INN,
    GET_OGRN,
    GET_DATETIME,
    GET_CREATIVE,
    ADMIN_REPLY
) = range(8)

user_data_dict = {}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("Кит для ума 🧠", callback_data='clever')],
        [InlineKeyboardButton("Explore China 🏯", callback_data='explore')]
    ]
    await update.message.reply_text(
        "Привет! 👋 Выберите канал и длительность рекламы:",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )
    return CHOOSING_PACKAGE

async def package_chosen(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    package = query.data
    user_data_dict[query.from_user.id] = {'package': package}
    await query.message.reply_text("Пожалуйста, введите ваше ФИО:")
    return GET_FULLNAME

async def get_fullname(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_data_dict[update.message.from_user.id]['fullname'] = update.message.text
    buttons = [["Самозанятый", "ИП", "ООО"]]
    await update.message.reply_text(
        "Выберите тип деятельности:",
        reply_markup=ReplyKeyboardMarkup(buttons, one_time_keyboard=True, resize_keyboard=True)
    )
    return GET_ACTIVITY

async def get_activity(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_data = user_data_dict[update.message.from_user.id]
    user_data['activity'] = update.message.text
    await update.message.reply_text("Пожалуйста, введите ваш ИНН:")
    return GET_INN

async def get_inn(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_data = user_data_dict[update.message.from_user.id]
    user_data['inn'] = update.message.text
    if user_data['activity'] == "Самозанятый":
        await update.message.reply_text("Введите дату и время рекламы:")
        return GET_DATETIME
    else:
        await update.message.reply_text("Введите ваш ОГРН/ОГРНИП:")
        return GET_OGRN

async def get_ogrn(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_data_dict[update.message.from_user.id]['ogrn'] = update.message.text
    await update.message.reply_text("Введите дату и время рекламы:")
    return GET_DATETIME

async def get_datetime(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_data_dict[update.message.from_user.id]['datetime'] = update.message.text
    await update.message.reply_text("Пришлите рекламный креатив (текст):")
    return GET_CREATIVE

async def get_creative(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_data = user_data_dict[update.message.from_user.id]
    user_data['creative'] = update.message.text

    message = f"📢 Новая заявка на рекламу:\n"               f"🔹 Пакет: {user_data['package']}\n"               f"👤 ФИО: {user_data['fullname']}\n"               f"🏷️ Тип: {user_data['activity']}\n"               f"🆔 ИНН: {user_data['inn']}\n"

    if 'ogrn' in user_data:
        message += f"📄 {'ОГРНИП' if user_data['activity'] == 'ИП' else 'ОГРН'}: {user_data['ogrn']}\n"

    message += f"📅 Дата и время: {user_data['datetime']}\n"                f"📣 Креатив: {user_data['creative']}"

    await context.bot.send_message(chat_id=ADMIN_CHAT_ID, text=message)
    await update.message.reply_text("Спасибо! Ваша заявка отправлена.")
    return ConversationHandler.END

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Отменено.")
    return ConversationHandler.END

async def startup_notify(application):
    await application.bot.send_message(chat_id=ADMIN_CHAT_ID, text="✅ Бот запущен и работает!")

if __name__ == '__main__':
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            CHOOSING_PACKAGE: [CallbackQueryHandler(package_chosen)],
            GET_FULLNAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_fullname)],
            GET_ACTIVITY: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_activity)],
            GET_INN: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_inn)],
            GET_OGRN: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_ogrn)],
            GET_DATETIME: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_datetime)],
            GET_CREATIVE: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_creative)],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
        per_message=True
    )

    app.add_handler(conv_handler)
    app.run_polling(after_startup=startup_notify)