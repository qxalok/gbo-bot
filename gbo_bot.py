#!/usr/bin/env python3
"""
Telegram-бот для лидогенерации ГБО (метан и пропан)
"""

import logging
from telegram import Update, ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    ConversationHandler,
    filters,
    ContextTypes,
)

# ========================
# НАСТРОЙКИ
# ========================
BOT_TOKEN = "8832172812:AAFUkWy5LhLkaLPRzuD-wLRzyz85pOrSeX0"
ADMIN_ID = 8046950575

# ========================
# ШАГИ ДИАЛОГА
# ========================
(
    GAS_TYPE,
    CAR_BRAND,
    CAR_YEAR,
    TOTAL_MILEAGE,
    ENGINE,
    CYLINDERS,
    NAME,
    PHONE,
) = range(8)

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)
logger = logging.getLogger(__name__)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    keyboard = [["⛽ Метан (КПГ)", "🔵 Пропан (СУГ)"]]
    reply_markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=True, resize_keyboard=True)
    await update.message.reply_text(
        "Привет! 👋\n\n"
        "Помогу подобрать газобаллонное оборудование и рассчитаю стоимость "
        "с учётом государственной субсидии.\n\n"
        "Для начала — какой газ вас интересует?",
        reply_markup=reply_markup
    )
    return GAS_TYPE


async def gas_type(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    choice = update.message.text
    context.user_data["gas_type"] = choice
    if "Метан" in choice:
        await update.message.reply_text(
            "✅ Метан — отличный выбор!\n\n"
            "Метан в среднем в 3,5 раза дешевле бензина. "
            "Плюс действует государственная субсидия которая значительно снижает стоимость установки.\n\n"
            "Напишите марку и модель вашего автомобиля.\n"
            "Например: <b>Toyota Camry</b> или <b>Lada Vesta</b>",
            reply_markup=ReplyKeyboardRemove(),
            parse_mode="HTML"
        )
    else:
        await update.message.reply_text(
            "✅ Пропан — хороший вариант!\n\n"
            "Пропан в среднем в 1,8 раза дешевле бензина. "
            "Установка подходит для большинства авто.\n\n"
            "Напишите марку и модель вашего автомобиля.\n"
            "Например: <b>Toyota Camry</b> или <b>Lada Vesta</b>",
            reply_markup=ReplyKeyboardRemove(),
            parse_mode="HTML"
        )
    return CAR_BRAND


async def car_brand(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data["car_brand"] = update.message.text
    await update.message.reply_text(
        "Укажите <b>год выпуска</b> автомобиля.\n"
        "Например: <b>2015</b>",
        parse_mode="HTML"
    )
    return CAR_YEAR


async def car_year(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    year_text = update.message.text.strip()
    if not year_text.isdigit() or not (1990 <= int(year_text) <= 2026):
        await update.message.reply_text("Пожалуйста, введите корректный год (например: 2015)")
        return CAR_YEAR

    context.user_data["car_year"] = year_text
    age = 2026 - int(year_text)
    context.user_data["car_age"] = age

    if age > 15 and "Метан" in context.user_data.get("gas_type", ""):
        await update.message.reply_text(
            f"⚠️ Вашему автомобилю {age} лет.\n\n"
            "К сожалению, государственная субсидия на метан распространяется только на авто "
            "<b>не старше 15 лет</b>.\n\n"
            "В этом случае <b>пропан будет выгоднее</b> — установка дешевле и субсидия не нужна. "
            "Наш специалист расскажет подробнее когда свяжется с вами.\n\n"
            "Продолжаем оформление заявки 👇\n\n"
            "Укажите <b>общий пробег</b> автомобиля (км).\n"
            "Например: <b>120000</b>",
            parse_mode="HTML"
        )
    else:
        await update.message.reply_text(
            "Укажите <b>общий пробег</b> автомобиля (км).\n"
            "Например: <b>120000</b>",
            parse_mode="HTML"
        )
    return TOTAL_MILEAGE


async def total_mileage(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data["total_mileage"] = update.message.text
    await update.message.reply_text(
        "Укажите <b>объём двигателя и мощность</b>.\n"
        "Например: <b>1.6 л, 110 л.с.</b>",
        parse_mode="HTML"
    )
    return ENGINE


async def engine(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data["engine"] = update.message.text
    keyboard = [["4 цилиндра", "6 цилиндров"], ["8 цилиндров", "Не знаю"]]
    reply_markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=True, resize_keyboard=True)
    await update.message.reply_text(
        "Сколько <b>цилиндров</b> у вашего двигателя?",
        reply_markup=reply_markup,
        parse_mode="HTML"
    )
    return CYLINDERS


async def cylinders(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data["cylinders"] = update.message.text
    await update.message.reply_text(
        "Как вас зовут?",
        reply_markup=ReplyKeyboardRemove()
    )
    return NAME


async def name(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data["name"] = update.message.text
    await update.message.reply_text(
        f"Приятно познакомиться, {update.message.text}! 👋\n\n"
        "Укажите ваш номер телефона.\n"
        "Например: <b>+79001234567</b>",
        parse_mode="HTML"
    )
    return PHONE


async def phone(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data["phone"] = update.message.text
    data = context.user_data
    gas = data.get("gas_type", "—")
    car = data.get("car_brand", "—")
    year = data.get("car_year", "—")
    total_km = data.get("total_mileage", "—")
    engine_val = data.get("engine", "—")
    cylinders_val = data.get("cylinders", "—")
    client_name = data.get("name", "—")
    phone_val = data.get("phone", "—")
    car_age = data.get("car_age", 0)

    # Определяем цену установки
    if "Метан" in gas:
        if "6" in cylinders_val or "8" in cylinders_val:
            install_cost = "от 100 000 ₽"
        else:
            install_cost = "от 80 000 ₽"
    else:
        install_cost = "от 45 000 ₽"

    # Определяем статус субсидии
    no_subsidy = "Метан" in gas and car_age > 15

    # Сообщение клиенту
    subsidy_note = ""
    if no_subsidy:
        subsidy_note = (
            "\n⚠️ По вашему авто субсидия на метан не применяется — возраст более 15 лет.\n"
            "Специалист расскажет почему в вашем случае <b>пропан может быть выгоднее</b>.\n"
        )

    await update.message.reply_text(
        f"✅ Спасибо, {client_name}! Заявка принята.\n\n"
        f"<b>Предварительный расчёт:</b>\n"
        f"• Тип газа: {gas}\n"
        f"• Ориентировочная стоимость установки: {install_cost}\n\n"
        f"{subsidy_note}"
        f"⚡ Точную стоимость вам назовёт специалист при звонке — "
        f"она может оказаться <b>ниже</b> ориентировочной.\n\n"
        "📌 <b>Важно:</b> в связи с высоким спросом на установку мы фиксируем запись "
        "только после внесения небольшого аванса — это гарантирует ваше место у мастера.\n"
        "• Аванс на карту физлица: <b>7 000 ₽</b>\n"
        "• Аванс на счёт ИП: <b>7 700 ₽</b>\n"
        "Реквизиты вышлет наш специалист. Аванс засчитывается в стоимость установки.\n\n"
        "Свяжемся с вами в течение 1-2 часов. 🚗",
        parse_mode="HTML"
    )

    # Статус субсидии для админа
    if "Метан" in gas:
        if car_age > 15:
            subsidy_status = "⚠️ Старше 15 лет — субсидия не положена. Рекомендовать пропан."
        else:
            subsidy_status = "✅ Подходит под субсидию"
    else:
        subsidy_status = "➖ Пропан — субсидия не применяется"

    lead_message = (
        f"🔥 <b>НОВЫЙ ЛИД — ГБО</b>\n\n"
        f"👤 Имя: {client_name}\n"
        f"📱 Телефон: {phone_val}\n\n"
        f"🚗 Авто: {car}\n"
        f"📅 Год: {year} ({car_age} лет)\n"
        f"🔧 Двигатель: {engine_val}\n"
        f"⚙️ Цилиндры: {cylinders_val}\n"
        f"⛽ Тип газа: {gas}\n"
        f"🛣 Общий пробег: {total_km} км\n\n"
        f"💰 Субсидия: {subsidy_status}\n"
        f"💵 Ориентировочная цена: {install_cost}\n\n"
        f"🆔 Telegram ID: {update.effective_user.id}\n"
        f"👤 Username: @{update.effective_user.username or 'не указан'}"
    )

    await context.bot.send_message(chat_id=ADMIN_ID, text=lead_message, parse_mode="HTML")
    return ConversationHandler.END


async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    await update.message.reply_text(
        "Хорошо. Если захотите вернуться — напишите /start",
        reply_markup=ReplyKeyboardRemove()
    )
    return ConversationHandler.END


def main() -> None:
    app = Application.builder().token(BOT_TOKEN).build()
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            GAS_TYPE:      [MessageHandler(filters.TEXT & ~filters.COMMAND, gas_type)],
            CAR_BRAND:     [MessageHandler(filters.TEXT & ~filters.COMMAND, car_brand)],
            CAR_YEAR:      [MessageHandler(filters.TEXT & ~filters.COMMAND, car_year)],
            TOTAL_MILEAGE: [MessageHandler(filters.TEXT & ~filters.COMMAND, total_mileage)],
            ENGINE:        [MessageHandler(filters.TEXT & ~filters.COMMAND, engine)],
            CYLINDERS:     [MessageHandler(filters.TEXT & ~filters.COMMAND, cylinders)],
            NAME:          [MessageHandler(filters.TEXT & ~filters.COMMAND, name)],
            PHONE:         [MessageHandler(filters.TEXT & ~filters.COMMAND, phone)],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )
    app.add_handler(conv_handler)
    print("✅ Бот запущен. Нажми Ctrl+C для остановки.")
    app.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
