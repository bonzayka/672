"""Конфигурация и тексты бота.

Секреты вшиты прямо сюда (без .env). Всё, что обычно меняют
(токен, админы, тарифы, реквизиты, тексты), — в этом файле.
"""

# ==================== Секреты ====================
# Токен от @BotFather.
# ВНИМАНИЕ: этот токен светился в публичном репозитории — если он
# перевыпускался через /revoke, замените строку ниже на актуальный.
BOT_TOKEN = "9142786482:AAGlH6IkMNbyd8mNBR04zmh6Y8dqClfZkUs"

# ID админов: им пересылаются квитанции, им доступны ✅/❌ и команда /admin.
# Узнать свой ID: отправьте боту команду /id
ADMIN_IDS = (6552268193, 7116116919)

# file_id стикера для /start (не обязательно).
# Хинт: переслать боту нужный стикер с админ-аккаунта — бот ответит его file_id.
STICKER_FILE_ID = ""


def is_admin(user_id: int) -> bool:
    return user_id in ADMIN_IDS


# ==================== Тарифы ====================
# Можно добавлять/менять сколько угодно записей — меню построится само.
# days — срок для учёта в статистике (36500 ≈ «навсегда»).
TARIFFS = [
    {
        "id": "week",
        "name_ru": "Приват на неделю",
        "name_en": "Private for a week",
        "duration_ru": "7 дней",
        "duration_en": "7 days",
        "price_rub": 1200,
        "price_usd": 15,
        "days": 7,
    },
    {
        "id": "month",
        "name_ru": "Приват на месяц",
        "name_en": "Private for a month",
        "duration_ru": "1 месяц",
        "duration_en": "1 month",
        "price_rub": 3000,
        "price_usd": 37,
        "days": 30,
    },
    {
        "id": "forever",
        "name_ru": "Приват навсегда",
        "name_en": "Private forever",
        "duration_ru": "бессрочно",
        "duration_en": "lifetime",
        "price_rub": 9000,
        "price_usd": 110,
        "days": 36500,
    },
]

TARIFFS_BY_ID = {t["id"]: t for t in TARIFFS}


def format_price(tariff: dict) -> str:
    """«3 000.00 RUB / 37 $» — снимок цены для текстов и БД."""
    rub = f"{tariff['price_rub']:,.2f}".replace(",", " ")
    return f"{rub} RUB / {tariff['price_usd']} $"


# ==================== Реквизиты оплаты ====================
# ЗАМЕНИТЕ на реальные реквизиты! Текст попадает и в сообщение,
# и в кнопку «Скопировать» (держите его в одну строку).
PAYMENT_METHOD_RU = "Карта (перевод)"
PAYMENT_METHOD_EN = "Card (transfer)"
PAYMENT_DETAILS = "0000 0000 0000 0000 — Банк, Имя Фамилия"

# ==================== Тексты (RU / EN) ====================
TEXTS = {
    "ru": {
        "choose_lang": "Выберите язык:",
        "continue": "Продолжить",
        "tariff_intro": "Чтобы ознакомиться с тарифом, выберите необходимый, нажав на соответствующую кнопку",
        "tariff_detail": (
            "Тариф: {name}\n"
            "Стоимость: {price}\n"
            "Срок действия: {duration}\n\n"
            "Вы получите доступ к следующим ресурсам: Приват (канал)"
        ),
        "pay_btn": "ОПЛАТИТЬ",
        "payment_info": (
            "Способ оплаты: {method}\n"
            "К оплате: {amount}\n"
            "Ваш ID: {user_id}\n\n"
            "Реквизиты для оплаты:\n\n"
            "Скопируй ⤵️\n\n"
            "{details}"
        ),
        "paid_btn": "Я ОПЛАТИЛ",
        "receipt_request": (
            "💁🏻‍♂️ Оплатили?\n\n"
            "👌🏻 Тогда отправьте сюда картинкой (не документом!) квитанцию платежа: скриншот или фото.\n\n"
            "На квитанции должны быть четко видны: дата, время и сумма платежа."
        ),
        "receipt_sent": "✅ Квитанция получена! Ожидайте подтверждения оплаты — мы свяжемся с вами.",
        "payment_approved": "✅ Оплата подтверждена! В ближайшее время мы свяжемся с вами и выдадим доступ.",
        "payment_rejected": (
            "❌ Квитанция отклонена. Если вы действительно произвели оплату — "
            "отправьте квитанцию повторно или свяжитесь с нами."
        ),
        "need_photo": (
            "❌ Пожалуйста, отправьте квитанцию картинкой (не документом!).\n"
            "На квитанции должны быть четко видны: дата, время и сумма платежа."
        ),
        "need_tariff_again": "⚠️ Не удалось определить тариф. Нажмите «ОПЛАТИТЬ» и «Я ОПЛАТИЛ» ещё раз.",
        "copy_btn": "📋 Скопировать реквизиты",
        "back": "Назад",
        "unknown": "Не понял 🤔 Используйте /start",
        "my_id": "🆔 Ваш ID: {user_id}",
    },
    "en": {
        "choose_lang": "Choose language:",
        "continue": "Continue",
        "tariff_intro": "To view the tariff, select the required one by pressing the corresponding button",
        "tariff_detail": (
            "Tariff: {name}\n"
            "Price: {price}\n"
            "Duration: {duration}\n\n"
            "You will get access to the following resources: Private (channel)"
        ),
        "pay_btn": "PAY",
        "payment_info": (
            "Payment method: {method}\n"
            "Amount to pay: {amount}\n"
            "Your ID: {user_id}\n\n"
            "Payment details:\n\n"
            "Copy ⤵️\n\n"
            "{details}"
        ),
        "paid_btn": "I HAVE PAID",
        "receipt_request": (
            "💁🏻‍♂️ Have you paid?\n\n"
            "👌🏻 Then send the payment receipt here as an image (not a document!): screenshot or photo.\n\n"
            "The receipt must clearly show: date, time and payment amount."
        ),
        "receipt_sent": "✅ Receipt received! Please wait for confirmation — we will contact you.",
        "payment_approved": "✅ Payment confirmed! We will contact you shortly to grant access.",
        "payment_rejected": (
            "❌ Receipt declined. If you actually paid, please send the receipt again or contact us."
        ),
        "need_photo": (
            "❌ Please send the receipt as an image (not a document!).\n"
            "The receipt must clearly show: date, time and payment amount."
        ),
        "need_tariff_again": "⚠️ Could not detect the tariff. Please tap PAY and then I HAVE PAID again.",
        "copy_btn": "📋 Copy payment details",
        "back": "Back",
        "unknown": "I don't understand 🤔 Use /start",
        "my_id": "🆔 Your ID: {user_id}",
    },
}

# ==================== Тексты админки (только для админов, RU) ====================
ADMIN_TEXTS = {
    "denied": "⛔ Доступ только для админов.",
    "new_receipt_caption": (
        "💳 Новая квитанция #{payment_id}\n"
        "👤 {full_name}{username}\n"
        "🆔 ID: {user_id}\n"
        "📦 Тариф: {tariff}\n"
        "💰 Сумма: {amount}\n"
        "🕒 {sent_at}{active_note}"
    ),
    "username_fmt": " (@{username})",
    "active_note_fmt": "\n⚠️ У юзера уже есть активная подписка до {expires}",
    "btn_approve": "✅ Подтвердить",
    "btn_reject": "❌ Отклонить",
    "already_processed": "Эта квитанция уже обработана.",
    "approved_done": "✅ Подтверждено. Юзер уведомлён.",
    "rejected_done": "❌ Отклонено. Юзер уведомлён.",
    "approved_mark": "\n\n✅ Подтверждено {time} — доступ до {expires}",
    "rejected_mark": "\n\n❌ Отклонено {time}",
    "sticker_hint": "file_id этого стикера:\n<code>{file_id}</code>",
}
