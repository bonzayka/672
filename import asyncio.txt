import asyncio
import logging
from aiogram import Bot, Dispatcher, F
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

# ==================== 配置 ====================
BOT_TOKEN = "9142786482:AAGlH6IkMNbyd8mNBR04zmh6Y8dqClfZkUs"  # замените на токен от @BotFather

# ВАЖНО: замените на реальный file_id стикера из набора demoness.
# Как получить: отправьте стикер боту, в логах найдите message.sticker.file_id
# Либо используйте get_sticker_set через API (требует дополнительной реализации).
STICKER_FILE_ID = "CAACAgIAAxkBAAE..."  # <-- замените

# Данные для оплаты (пример)
PAYMENT_ADDRESS = "TWg3Hfi7VcbE76NpYSERCyqLJ6tqjK7yED"

# ==================== Тексты ====================
TEXTS = {
    "ru": {
        "choose_lang": "Выберите язык:",
        "lang_btn": "Language: RU",
        "continue": "Продолжить",
        "tariff_intro": "Чтобы ознакомиться с тарифом, выберите необходимый, нажав на соответствующую кнопку",
        "tariff_private": "Приват на месяц",
        "tariff_detail": (
            "Тариф: Приват на месяц\n"
            "Стоимость: 3 000.00 RUB / 37 $\n"
            "Срок действия: 1 месяц\n\n"
            "Вы получите доступ к следующим ресурсам: Приват (канал)"
        ),
        "pay_btn": "ОПЛАТИТЬ",
        "choose_payment": "Выберите способ оплаты:",
        "usdt_trc20": "USDT TRC20",
        "payment_info": (
            "Способ оплаты: USDT TRC20\n"
            "К оплате: 3 000.00 RUB / 37 $\n"
            "Ваш ID: {user_id}\n\n"
            "Реквизиты для оплаты:\n\n"
            "Скопируй ⤵️ адрес\n\n"
            "{address}"
        ),
        "paid_btn": "Я ОПЛАТИЛ",
        "receipt_request": (
            "💁🏻‍♂️ Оплатили?\n\n"
            "👌🏻 Тогда отправьте сюда картинкой (не документом!) квитанцию платежа: скриншот или фото.\n\n"
            "На квитанции должны быть четко видны: дата, время и сумма платежа."
        ),
        "copy_hint": "Скопируй ⤵️ адрес",
        "back": "Назад",
    },
    "en": {
        "choose_lang": "Choose language:",
        "lang_btn": "Language: EN",
        "continue": "Continue",
        "tariff_intro": "To view the tariff, select the required one by pressing the corresponding button",
        "tariff_private": "Private for a month",
        "tariff_detail": (
            "Tariff: Private for a month\n"
            "Price: 3 000.00 RUB / $37\n"
            "Duration: 1 month\n\n"
            "You will get access to the following resources: Private (channel)"
        ),
        "pay_btn": "PAY",
        "choose_payment": "Choose payment method:",
        "usdt_trc20": "USDT TRC20",
        "payment_info": (
            "Payment method: USDT TRC20\n"
            "Amount to pay: 3 000.00 RUB / $37\n"
            "Your ID: {user_id}\n\n"
            "Payment details:\n\n"
            "Copy ⤵️ address\n\n"
            "{address}"
        ),
        "paid_btn": "I HAVE PAID",
        "receipt_request": (
            "💁🏻‍♂️ Have you paid?\n\n"
            "👌🏻 Then send the payment receipt here as an image (not a document!): screenshot or photo.\n\n"
            "The receipt must clearly show: date, time and payment amount."
        ),
        "copy_hint": "Copy ⤵️ address",
        "back": "Back",
    }
}

# ==================== Инициализация ====================
logging.basicConfig(level=logging.INFO)
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

# Хранилище выбранного языка (в реальном проекте используйте БД/Redis)
user_lang: dict[int, str] = {}


def t(user_id: int, key: str, **kwargs) -> str:
    """Получить текст на языке пользователя."""
    lang = user_lang.get(user_id, "ru")
    text = TEXTS[lang][key]
    if kwargs:
        text = text.format(**kwargs)
    return text


# ==================== Клавиатуры ====================

def kb_language(user_id: int) -> InlineKeyboardMarkup:
    """Клавиатура выбора языка (RU -> EN при нажатии)."""
    lang = user_lang.get(user_id, "ru")
    # Кнопка показывает ПРОТИВОПОЛОЖНЫЙ язык для переключения,
    # но в задании сказано: "кнопка Language: RU ... а если нажать ... Language: EN"
    # Т.е. изначально RU, при нажатии становится EN (переключение).
    # Показываем текущий язык на кнопке (как в описании: сначала "Language: RU").
    btn_text = "Language: RU" if lang == "ru" else "Language: EN"
    builder = InlineKeyboardBuilder()
    builder.button(text=btn_text, callback_data="switch_lang")
    return builder.as_markup()


def kb_continue(user_id: int) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(text=t(user_id, "continue"), callback_data="continue")
    return builder.as_markup()


def kb_tariffs(user_id: int) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(text=t(user_id, "tariff_private"), callback_data="tariff_private")
    return builder.as_markup()


def kb_pay(user_id: int) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(text=t(user_id, "pay_btn"), callback_data="pay")
    return builder.as_markup()


def kb_payment_method(user_id: int) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(text="USDT TRC20", callback_data="pay_usdt")
    builder.button(text=t(user_id, "back"), callback_data="back_to_tariff")
    return builder.as_markup()


def kb_paid(user_id: int) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(text=t(user_id, "paid_btn"), callback_data="paid")
    return builder.as_markup()


# ==================== Обработчики ====================

@dp.message(Command("start"))
async def cmd_start(message: Message):
    """Команда /start: отправляем стикер и кнопку языка."""
    user_lang[message.from_user.id] = "ru"  # по умолчанию русский

    # 1. Отправляем стикер
    try:
        await message.answer_sticker(sticker=STICKER_FILE_ID)
    except Exception as e:
        logging.warning(f"Не удалось отправить стикер: {e}")
        # Если file_id неверный, можно отправить сообщение-заглушку
        await message.answer("🎭 (sticker demoness)")

    # 2. Отправляем сообщение с кнопкой языка
    await message.answer(
        text=t(message.from_user.id, "choose_lang"),
        reply_markup=kb_language(message.from_user.id),
    )


@dp.callback_query(F.data == "switch_lang")
async def switch_language(call: CallbackQuery):
    """Переключение языка RU <-> EN."""
    user_id = call.from_user.id
    current = user_lang.get(user_id, "ru")
    new_lang = "en" if current == "ru" else "ru"
    user_lang[user_id] = new_lang

    # Обновляем сообщение с кнопкой языка
    await call.message.edit_text(
        text=t(user_id, "choose_lang"),
        reply_markup=kb_language(user_id),
    )
    # Добавляем кнопку "Продолжить" (как в задании: после переключения появляется вторая кнопка)
    # Отправляем новое сообщение с кнопкой Continue
    await call.message.answer(
        text="👇",
        reply_markup=kb_continue(user_id),
    )
    await call.answer()


@dp.callback_query(F.data == "continue")
async def on_continue(call: CallbackQuery):
    """Нажатие 'Продолжить' -> показываем интро тарифов и кнопку тарифа."""
    user_id = call.from_user.id
    await call.message.edit_text(
        text=t(user_id, "tariff_intro"),
        reply_markup=kb_tariffs(user_id),
    )
    await call.answer()


@dp.callback_query(F.data == "tariff_private")
async def on_tariff_private(call: CallbackQuery):
    """Показ деталей тарифа 'Приват на месяц'."""
    user_id = call.from_user.id
    await call.message.edit_text(
        text=t(user_id, "tariff_detail"),
        reply_markup=kb_pay(user_id),
    )
    await call.answer()


@dp.callback_query(F.data == "pay")
async def on_pay(call: CallbackQuery):
    """Нажатие ОПЛАТИТЬ -> выбор способа оплаты."""
    user_id = call.from_user.id
    await call.message.edit_text(
        text=t(user_id, "tariff_detail") + "\n\n" + t(user_id, "choose_payment"),
        reply_markup=kb_payment_method(user_id),
    )
    await call.answer()


@dp.callback_query(F.data == "pay_usdt")
async def on_pay_usdt(call: CallbackQuery):
    """Показ реквизитов USDT TRC20 и кнопки 'Я оплатил'."""
    user_id = call.from_user.id
    text = t(user_id, "payment_info", user_id=user_id, address=PAYMENT_ADDRESS)
    # Экранирование не нужно для обычного текста (без parse_mode)
    await call.message.edit_text(
        text=text,
        reply_markup=kb_paid(user_id),
    )
    await call.answer()


@dp.callback_query(F.data == "paid")
async def on_paid(call: CallbackQuery):
    """Нажатие 'Я ОПЛАТИЛ' -> запрос квитанции."""
    user_id = call.from_user.id
    await call.message.edit_text(
        text=t(user_id, "receipt_request"),
        reply_markup=None,  # убираем клавиатуру
    )
    await call.answer()


@dp.callback_query(F.data == "back_to_tariff")
async def back_to_tariff(call: CallbackQuery):
    """Возврат к деталям тарифа."""
    user_id = call.from_user.id
    await call.message.edit_text(
        text=t(user_id, "tariff_detail"),
        reply_markup=kb_pay(user_id),
    )
    await call.answer()


@dp.message(F.photo | F.document)
async def handle_receipt(message: Message):
    """Обработка присланной квитанции (фото или документ)."""
    user_id = message.from_user.id
    if message.document:
        await message.answer(
            "❌ Пожалуйста, отправьте квитанцию как **фото** (не документом).\n"
            "Попробуйте ещё раз, выбрав изображение из галереи."
        )
        return

    # Здесь можно добавить логику сохранения/пересылки админу
    await message.answer(
        "✅ Квитанция получена! Ожидайте подтверждения оплаты.\n"
        "Мы свяжемся с вами после проверки."
    )


# ==================== Запуск ====================

async def main():
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main()) No newline at end of file