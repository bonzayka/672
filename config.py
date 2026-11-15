"""Конфигурация и тексты бота.

Секреты вшиты прямо сюда (без .env). Всё, что обычно меняют
(токен, админы, тарифы, реквизиты, тексты), — в этом файле.
"""

# ==================== Секреты ====================
# Токен от @BotFather.
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
        "name_ru": "🔥 Приват на неделю",
        "name_en": "🔥 Private for a week",
        "duration_ru": "7 дней",
        "duration_en": "7 days",
        "price_rub": 1200,
        "price_usd": 15,
        "days": 7,
        "emoji": "⚡",
        "desc_ru": "Быстрый старт — попробуй и оцени",
        "desc_en": "Quick start — try it and decide",
    },
    {
        "id": "month",
        "name_ru": "💎 Приват на месяц",
        "name_en": "💎 Private for a month",
        "duration_ru": "1 месяц",
        "duration_en": "1 month",
        "price_rub": 3000,
        "price_usd": 37,
        "days": 30,
        "emoji": "🏆",
        "desc_ru": "Самый популярный — выгоднее на 20%",
        "desc_en": "Most popular — 20% better value",
    },
    {
        "id": "forever",
        "name_ru": "👑 Приват навсегда",
        "name_en": "👑 Private forever",
        "duration_ru": "бессрочно",
        "duration_en": "lifetime",
        "price_rub": 9000,
        "price_usd": 110,
        "days": 36500,
        "emoji": "♾",
        "desc_ru": "Максимум привилегий — навечно",
        "desc_en": "Maximum privileges — forever",
    },
]

TARIFFS_BY_ID = {t["id"]: t for t in TARIFFS}


def format_price(tariff: dict) -> str:
    """«3 000.00 RUB / 37 $» — снимок цены для текстов и БД."""
    rub = f"{tariff['price_rub']:,.2f}".replace(",", " ")
    return f"{rub} RUB / {tariff['price_usd']} $"


def short_price(tariff: dict) -> str:
    """Краткая цена для кнопок: «1 200₽ / 15$»."""
    rub = f"{tariff['price_rub']:,}".replace(",", " ")
    return f"{rub}₽ / {tariff['price_usd']}$"


# ==================== Реквизиты оплаты ====================
PAYMENT_METHOD_RU = "💳 Карта (перевод)"
PAYMENT_METHOD_EN = "💳 Card (transfer)"
PAYMENT_DETAILS = "0000 0000 0000 0000 — Банк, Имя Фамилия"

# ==================== Тексты (RU / EN) ====================
TEXTS = {
    "ru": {
        # /start — приветствие
        "welcome": (
            "━━━━━━━━━━━━━━━━━━━━\n"
            "       🌟 <b>Добро пожаловать!</b> 🌟\n"
            "━━━━━━━━━━━━━━━━━━━━\n\n"
            "Здесь ты можешь оформить подписку\n"
            "на наш <b>приватный канал</b> 🔐\n\n"
            "Эксклюзивный контент ждёт тебя!\n\n"
            "⬇️ Выбери язык и нажми <b>Продолжить</b>"
        ),
        "choose_lang": "🌐 <b>Язык интерфейса</b>",
        "continue": "▶️ Продолжить",
        "tariff_intro": (
            "━━━━━━━━━━━━━━━━━━━━\n"
            "       📋 <b>Выбери тариф</b>\n"
            "━━━━━━━━━━━━━━━━━━━━\n\n"
            "Нажми на тариф, чтобы узнать\n"
            "подробности и перейти к оплате 👇"
        ),
        "tariff_detail": (
            "━━━━━━━━━━━━━━━━━━━━\n"
            "  {emoji} <b>{name}</b>\n"
            "━━━━━━━━━━━━━━━━━━━━\n\n"
            "💰 <b>Стоимость:</b> {price}\n"
            "⏳ <b>Срок:</b> {duration}\n\n"
            "📌 <i>{desc}</i>\n\n"
            "Вы получите доступ к:\n"
            "  🔐 Приватный канал\n"
            "  🎁 Эксклюзивный контент\n"
            "  ⚡ Мгновенная выдача\n\n"
            "Готовы? Нажмите <b>ОПЛАТИТЬ</b> 👇"
        ),
        "pay_btn": "💳 ОПЛАТИТЬ",
        "payment_info": (
            "━━━━━━━━━━━━━━━━━━━━\n"
            "     💳 <b>Оплата подписки</b>\n"
            "━━━━━━━━━━━━━━━━━━━━\n\n"
            "📝 <b>Способ:</b> {method}\n"
            "💰 <b>К оплате:</b> {amount}\n"
            "🆔 <b>Ваш ID:</b> <code>{user_id}</code>\n\n"
            "━━━━━━━━━━━━━━━━━━━━\n"
            "📎 <b>Реквизиты для перевода:</b>\n\n"
            "<code>{details}</code>\n\n"
            "━━━━━━━━━━━━━━━━━━━━\n\n"
            "❗ <b>Важно:</b> в комментарии к переводу\n"
            "укажите ваш ID: <code>{user_id}</code>"
        ),
        "paid_btn": "✅ Я ОПЛАТИЛ",
        "receipt_request": (
            "━━━━━━━━━━━━━━━━━━━━\n"
            "     📸 <b>Отправьте квитанцию</b>\n"
            "━━━━━━━━━━━━━━━━━━━━\n\n"
            "Оплатили? Отлично! 👍\n\n"
            "Отправьте сюда <b>скриншот</b> или <b>фото</b>\n"
            "квитанции <u>картинкой</u> (не документом!)\n\n"
            "На квитанции должны быть видны:\n"
            "  📅 Дата и время\n"
            "  💰 Сумма платежа\n"
            "  ✅ Статус «Выполнено»"
        ),
        "receipt_sent": (
            "━━━━━━━━━━━━━━━━━━━━\n"
            "    ✅ <b>Квитанция получена!</b>\n"
            "━━━━━━━━━━━━━━━━━━━━\n\n"
            "⏳ Ожидайте подтверждения оплаты.\n"
            "Обычно это занимает до 15 минут.\n\n"
            "Мы уведомим вас сразу после проверки! 🔔"
        ),
        "payment_approved": (
            "━━━━━━━━━━━━━━━━━━━━\n"
            "   🎉 <b>Оплата подтверждена!</b> 🎉\n"
            "━━━━━━━━━━━━━━━━━━━━\n\n"
            "Добро пожаловать в приват! 🔐\n\n"
            "В ближайшее время мы выдадим\n"
            "вам доступ к каналу.\n\n"
            "Спасибо за доверие! 💜"
        ),
        "payment_rejected": (
            "━━━━━━━━━━━━━━━━━━━━\n"
            "   ❌ <b>Квитанция отклонена</b>\n"
            "━━━━━━━━━━━━━━━━━━━━\n\n"
            "Если вы произвели оплату — отправьте\n"
            "квитанцию повторно или свяжитесь\n"
            "с администрацией.\n\n"
            "💡 Убедитесь, что на скриншоте чётко\n"
            "видны дата, время и сумма."
        ),
        "need_photo": (
            "⚠️ Пожалуйста, отправьте квитанцию\n"
            "<b>картинкой</b> (не документом!)\n\n"
            "На квитанции должны быть видны:\n"
            "  📅 Дата и время\n"
            "  💰 Сумма платежа"
        ),
        "need_tariff_again": "⚠️ Не удалось определить тариф. Нажмите «ОПЛАТИТЬ» и «Я ОПЛАТИЛ» ещё раз.",
        "copy_btn": "📋 Скопировать реквизиты",
        "back": "◀️ Назад",
        "unknown": "🤔 Не понимаю. Используйте /start для начала.",
        "my_id": "🆔 <b>Ваш ID:</b> <code>{user_id}</code>",
        # /profile
        "profile_active": (
            "━━━━━━━━━━━━━━━━━━━━\n"
            "       👤 <b>Ваш профиль</b>\n"
            "━━━━━━━━━━━━━━━━━━━━\n\n"
            "🆔 ID: <code>{user_id}</code>\n"
            "📦 Тариф: <b>{tariff}</b>\n"
            "📅 Активна до: <b>{expires}</b>\n"
            "✅ Статус: <b>Активна</b>\n\n"
            "Наслаждайтесь контентом! 🎉"
        ),
        "profile_inactive": (
            "━━━━━━━━━━━━━━━━━━━━\n"
            "       👤 <b>Ваш профиль</b>\n"
            "━━━━━━━━━━━━━━━━━━━━\n\n"
            "🆔 ID: <code>{user_id}</code>\n"
            "📦 Подписка: <b>Нет</b>\n\n"
            "Оформите подписку через /start 💫"
        ),
        # /help
        "help": (
            "━━━━━━━━━━━━━━━━━━━━\n"
            "       ❓ <b>Помощь</b>\n"
            "━━━━━━━━━━━━━━━━━━━━\n\n"
            "📌 <b>Доступные команды:</b>\n\n"
            "  /start — Начать / Купить подписку\n"
            "  /profile — Моя подписка\n"
            "  /id — Узнать свой ID\n"
            "  /help — Эта справка\n\n"
            "━━━━━━━━━━━━━━━━━━━━\n"
            "📝 <b>Как купить подписку:</b>\n\n"
            "1️⃣ Нажмите /start\n"
            "2️⃣ Выберите тариф\n"
            "3️⃣ Нажмите «ОПЛАТИТЬ»\n"
            "4️⃣ Переведите оплату по реквизитам\n"
            "5️⃣ Нажмите «Я ОПЛАТИЛ»\n"
            "6️⃣ Отправьте скриншот квитанции\n"
            "7️⃣ Дождитесь подтверждения ✅\n\n"
            "По вопросам — обращайтесь\n"
            "к администратору 💬"
        ),
    },
    "en": {
        "welcome": (
            "━━━━━━━━━━━━━━━━━━━━\n"
            "       🌟 <b>Welcome!</b> 🌟\n"
            "━━━━━━━━━━━━━━━━━━━━\n\n"
            "Here you can subscribe to\n"
            "our <b>private channel</b> 🔐\n\n"
            "Exclusive content awaits you!\n\n"
            "⬇️ Choose language and tap <b>Continue</b>"
        ),
        "choose_lang": "🌐 <b>Interface language</b>",
        "continue": "▶️ Continue",
        "tariff_intro": (
            "━━━━━━━━━━━━━━━━━━━━\n"
            "       📋 <b>Choose a plan</b>\n"
            "━━━━━━━━━━━━━━━━━━━━\n\n"
            "Tap a plan to see details\n"
            "and proceed to payment 👇"
        ),
        "tariff_detail": (
            "━━━━━━━━━━━━━━━━━━━━\n"
            "  {emoji} <b>{name}</b>\n"
            "━━━━━━━━━━━━━━━━━━━━\n\n"
            "💰 <b>Price:</b> {price}\n"
            "⏳ <b>Duration:</b> {duration}\n\n"
            "📌 <i>{desc}</i>\n\n"
            "You will get access to:\n"
            "  🔐 Private channel\n"
            "  🎁 Exclusive content\n"
            "  ⚡ Instant access\n\n"
            "Ready? Tap <b>PAY</b> below 👇"
        ),
        "pay_btn": "💳 PAY",
        "payment_info": (
            "━━━━━━━━━━━━━━━━━━━━\n"
            "     💳 <b>Payment</b>\n"
            "━━━━━━━━━━━━━━━━━━━━\n\n"
            "📝 <b>Method:</b> {method}\n"
            "💰 <b>Amount:</b> {amount}\n"
            "🆔 <b>Your ID:</b> <code>{user_id}</code>\n\n"
            "━━━━━━━━━━━━━━━━━━━━\n"
            "📎 <b>Payment details:</b>\n\n"
            "<code>{details}</code>\n\n"
            "━━━━━━━━━━━━━━━━━━━━\n\n"
            "❗ <b>Important:</b> include your ID\n"
            "in the transfer comment: <code>{user_id}</code>"
        ),
        "paid_btn": "✅ I HAVE PAID",
        "receipt_request": (
            "━━━━━━━━━━━━━━━━━━━━\n"
            "     📸 <b>Send your receipt</b>\n"
            "━━━━━━━━━━━━━━━━━━━━\n\n"
            "Paid? Great! 👍\n\n"
            "Send a <b>screenshot</b> or <b>photo</b>\n"
            "of your receipt as an <u>image</u> (not a file!)\n\n"
            "The receipt must show:\n"
            "  📅 Date and time\n"
            "  💰 Payment amount\n"
            "  ✅ Status «Completed»"
        ),
        "receipt_sent": (
            "━━━━━━━━━━━━━━━━━━━━\n"
            "    ✅ <b>Receipt received!</b>\n"
            "━━━━━━━━━━━━━━━━━━━━\n\n"
            "⏳ Waiting for confirmation.\n"
            "Usually takes up to 15 minutes.\n\n"
            "We'll notify you right away! 🔔"
        ),
        "payment_approved": (
            "━━━━━━━━━━━━━━━━━━━━\n"
            "   🎉 <b>Payment confirmed!</b> 🎉\n"
            "━━━━━━━━━━━━━━━━━━━━\n\n"
            "Welcome to the private channel! 🔐\n\n"
            "We will grant you access shortly.\n\n"
            "Thank you for your trust! 💜"
        ),
        "payment_rejected": (
            "━━━━━━━━━━━━━━━━━━━━\n"
            "   ❌ <b>Receipt declined</b>\n"
            "━━━━━━━━━━━━━━━━━━━━\n\n"
            "If you actually paid — please send\n"
            "the receipt again or contact\n"
            "the administrator.\n\n"
            "💡 Make sure the screenshot clearly\n"
            "shows date, time and amount."
        ),
        "need_photo": (
            "⚠️ Please send the receipt\n"
            "as an <b>image</b> (not a file!)\n\n"
            "The receipt must show:\n"
            "  📅 Date and time\n"
            "  💰 Payment amount"
        ),
        "need_tariff_again": "⚠️ Could not detect the tariff. Please tap PAY and then I HAVE PAID again.",
        "copy_btn": "📋 Copy payment details",
        "back": "◀️ Back",
        "unknown": "🤔 I don't understand. Use /start to begin.",
        "my_id": "🆔 <b>Your ID:</b> <code>{user_id}</code>",
        "profile_active": (
            "━━━━━━━━━━━━━━━━━━━━\n"
            "       👤 <b>Your profile</b>\n"
            "━━━━━━━━━━━━━━━━━━━━\n\n"
            "🆔 ID: <code>{user_id}</code>\n"
            "📦 Plan: <b>{tariff}</b>\n"
            "📅 Active until: <b>{expires}</b>\n"
            "✅ Status: <b>Active</b>\n\n"
            "Enjoy the content! 🎉"
        ),
        "profile_inactive": (
            "━━━━━━━━━━━━━━━━━━━━\n"
            "       👤 <b>Your profile</b>\n"
            "━━━━━━━━━━━━━━━━━━━━\n\n"
            "🆔 ID: <code>{user_id}</code>\n"
            "📦 Subscription: <b>None</b>\n\n"
            "Get a subscription via /start 💫"
        ),
        "help": (
            "━━━━━━━━━━━━━━━━━━━━\n"
            "       ❓ <b>Help</b>\n"
            "━━━━━━━━━━━━━━━━━━━━\n\n"
            "📌 <b>Available commands:</b>\n\n"
            "  /start — Start / Buy subscription\n"
            "  /profile — My subscription\n"
            "  /id — Get your ID\n"
            "  /help — This help page\n\n"
            "━━━━━━━━━━━━━━━━━━━━\n"
            "📝 <b>How to subscribe:</b>\n\n"
            "1️⃣ Tap /start\n"
            "2️⃣ Choose a plan\n"
            "3️⃣ Tap «PAY»\n"
            "4️⃣ Transfer the payment\n"
            "5️⃣ Tap «I HAVE PAID»\n"
            "6️⃣ Send a receipt screenshot\n"
            "7️⃣ Wait for confirmation ✅\n\n"
            "For questions — contact\n"
            "the administrator 💬"
        ),
    },
}

# ==================== Тексты админки (только для админов, RU) ====================
ADMIN_TEXTS = {
    "denied": "⛔ Доступ только для админов.",
    "new_receipt_caption": (
        "━━━━━━━━━━━━━━━━━━━━\n"
        "  💳 <b>Квитанция #{payment_id}</b>\n"
        "━━━━━━━━━━━━━━━━━━━━\n\n"
        "👤 {full_name}{username}\n"
        "🆔 ID: <code>{user_id}</code>\n"
        "📦 Тариф: <b>{tariff}</b>\n"
        "💰 Сумма: <b>{amount}</b>\n"
        "🕒 {sent_at}{active_note}"
    ),
    "username_fmt": " (<a href='tg://user?id={user_id}'>@{username}</a>)",
    "active_note_fmt": "\n\n⚠️ <b>У юзера уже есть подписка до {expires}</b>",
    "btn_approve": "✅ Подтвердить",
    "btn_reject": "❌ Отклонить",
    "already_processed": "Эта квитанция уже обработана.",
    "approved_done": "✅ Подтверждено. Юзер уведомлён.",
    "rejected_done": "❌ Отклонено. Юзер уведомлён.",
    "approved_mark": "\n\n✅ <b>Подтверждено</b> {time}\n📅 Доступ до {expires}",
    "rejected_mark": "\n\n❌ <b>Отклонено</b> {time}",
    "sticker_hint": "file_id этого стикера:\n<code>{file_id}</code>",
    "admin_header": (
        "━━━━━━━━━━━━━━━━━━━━\n"
        "     📊 <b>Панель администратора</b>\n"
        "━━━━━━━━━━━━━━━━━━━━\n"
    ),
}
