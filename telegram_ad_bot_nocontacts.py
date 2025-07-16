import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, ConversationHandler, MessageHandler, filters, ContextTypes

BOT_TOKEN = "7588445095:AAFbowVOxKispj00FfKmBKrKRfQxQTKyt44"
ADMIN_CHAT_ID = 672260476

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

(
    CHOOSING_CHANNEL,
    ASK_FULL_NAME,
    ASK_ACTIVITY,
    ASK_INN,
    ASK_OGRN,
    ASK_DATE,
    ASK_CREATIVE,
) = range(7)

user_data_store = {}

keyboard = [
    [InlineKeyboardButton("Кит для ума – 1000/24ч", callback_data="cleverchinese_24")],
    [InlineKeyboardButton("Кит для ума – 1600/48ч", callback_data="cleverchinese_48")],
    [InlineKeyboardButton("Кит для ума – 2600/неделя", callback_data="cleverchinese_week")],
    [InlineKeyboardButton("Explore China – 800/24ч", callback_data="explorezhongguo_24")],
    [InlineKeyboardButton("Explore China – 1300/48ч", callback_data="explorezhongguo_48")],
    [InlineKeyboardButton("Explore China – 2000/неделя", callback_data="explorezhongguo_week")],
]

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("👋 Здравствуйте! Выберите вариант рекламы:", reply_markup=InlineKeyboardMarkup(keyboard))
    return CHOOSING_CHANNEL

async def choose_channel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_data_store[query.from_user.id] = {"channel_option": query.data}
    await query.message.reply_text("Введите ваше ФИО:")
    return ASK_FULL_NAME

async def ask_full_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_data_store[update.message.from_user.id]["full_name"] = update.message.text
    await update.message.reply_text("Выберите тип деятельности: Самозанятый, ИП, ООО")
    return ASK_ACTIVITY

async def ask_activity(update: Update, context: ContextTypes.DEFAULT_TYPE):
    activity = update.message.text
    user_data_store[update.message.from_user.id]["activity"] = activity
    await update.message.reply_text("Введите ваш ИНН:")
    return ASK_INN

async def ask_inn(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_data_store[update.message.from_user.id]["inn"] = update.message.text
    activity = user_data_store[update.message.from_user.id]["activity"]
    if activity == "ИП":
        await update.message.reply_text("Введите ваш ОГРНИП:")
    elif activity == "ООО":
        await update.message.reply_text("Введите ваш ОГРН:")
    else:
        await update.message.reply_text("Укажите дату и время публикации рекламы:")
        return ASK_DATE
    return ASK_OGRN

async def ask_ogrn(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_data_store[update.message.from_user.id]["ogrn"] = update.message.text
    await update.message.reply_text("Укажите дату и время публикации рекламы:")
    return ASK_DATE

async def ask_date(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_data_store[update.message.from_user.id]["date"] = update.message.text
    await update.message.reply_text("Отправьте текст или изображение рекламного креатива:")
    return ASK_CREATIVE

async def ask_creative(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_data = user_data_store[update.message.from_user.id]
    user_data["creative"] = update.message.text if update.message.text else "изображение"

    message = (
        f"📢 Новая заявка на рекламу:"
        f"👤 ФИО: {user_data['full_name']}"
        f"📦 Канал и формат: {user_data['channel_option']}"
        f"💼 Деятельность: {user_data['activity']}"
        f"🧾 ИНН: {user_data['inn']}"
    )
    if "ogrn" in user_data:
        message += f"📄 {'ОГРНИП' if user_data['activity'] == 'ИП' else 'ОГРН'}: {user_data['ogrn']}"
    message += f"🗓 Дата и время рекламы: {user_data['date']}"
    message += f"📝 Креатив: {user_data['creative']}"

    await context.bot.send_message(chat_id=ADMIN_CHAT_ID, text=message)
    await update.message.reply_text("✅ Спасибо! Заявка отправлена оператору.")
    return ConversationHandler.END

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Заявка отменена.")
    return ConversationHandler.END

def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            CHOOSING_CHANNEL: [CallbackQueryHandler(choose_channel)],
            ASK_FULL_NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, ask_full_name)],
            ASK_ACTIVITY: [MessageHandler(filters.TEXT & ~filters.COMMAND, ask_activity)],
            ASK_INN: [MessageHandler(filters.TEXT & ~filters.COMMAND, ask_inn)],
            ASK_OGRN: [MessageHandler(filters.TEXT & ~filters.COMMAND, ask_ogrn)],
            ASK_DATE: [MessageHandler(filters.TEXT & ~filters.COMMAND, ask_date)],
            ASK_CREATIVE: [MessageHandler(filters.ALL, ask_creative)],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )

    app.add_handler(conv_handler)
    app.run_polling()

if __name__ == "__main__":
    main()