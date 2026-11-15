"""Бот продажи подписки: воронка, приём квитанций, админка.

Запуск: python bot.py  (токен, админы и тарифы — в config.py)

Флоу юзера:
/start -> выбор языка -> продолжить -> тариф -> ОПЛАТИТЬ -> реквизиты ->
Я ОПЛАТИЛ -> фото квитанции -> админ одобряет -> юзер получает уведомление.
"""
import asyncio
import logging
from datetime import datetime

from aiogram import Bot, Dispatcher, F
from aiogram.client.default import DefaultBotProperties
from aiogram.exceptions import TelegramBadRequest
from aiogram.filters import Command, CommandStart
from aiogram.types import (
    CallbackQuery,
    CopyTextButton,
    InlineKeyboardMarkup,
    Message,
)
from aiogram.utils.keyboard import InlineKeyboardBuilder

import db
from config import (
    ADMIN_IDS,
    ADMIN_TEXTS,
    BOT_TOKEN,
    PAYMENT_DETAILS,
    PAYMENT_METHOD_EN,
    PAYMENT_METHOD_RU,
    STICKER_FILE_ID,
    TARIFFS,
    TARIFFS_BY_ID,
    TEXTS,
    format_price,
    is_admin,
    short_price,
)

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s: %(message)s")
log = logging.getLogger("bot")

dp = Dispatcher()

STATUS_EMOJI = {"pending": "⏳", "approved": "✅", "rejected": "❌"}


# ==================== Хелперы ====================

def t(lang: str, key: str, **kwargs) -> str:
    text = TEXTS[lang][key]
    return text.format(**kwargs) if kwargs else text


def lang_name(tariff: dict, lang: str) -> str:
    return tariff["name_ru" if lang == "ru" else "name_en"]


def lang_duration(tariff: dict, lang: str) -> str:
    return tariff["duration_ru" if lang == "ru" else "duration_en"]


def lang_desc(tariff: dict, lang: str) -> str:
    return tariff["desc_ru" if lang == "ru" else "desc_en"]


def lang_method(lang: str) -> str:
    return PAYMENT_METHOD_RU if lang == "ru" else PAYMENT_METHOD_EN


async def safe_edit(message: Message, text: str, reply_markup: InlineKeyboardMarkup | None = None) -> None:
    """edit_text с обработкой «message is not modified» и недоступных сообщений."""
    try:
        await message.edit_text(text, reply_markup=reply_markup)
    except TelegramBadRequest as e:
        if "not modified" in str(e).lower():
            return
        log.warning("edit_text не удался (%s) — отправляю новое сообщение", e)
        await message.answer(text, reply_markup=reply_markup)


# ==================== Клавиатуры ====================

_LANG_FLAGS = {"ru": "🇷🇺 Русский", "en": "🇬🇧 English"}


def kb_language(lang: str) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    other = "en" if lang == "ru" else "ru"
    builder.button(text=f"✦ {_LANG_FLAGS[lang]}", callback_data="noop")
    builder.button(text=f"→ {_LANG_FLAGS[other]}", callback_data="switch_lang")
    builder.adjust(2)
    return builder.as_markup()


def kb_continue(lang: str) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(text=t(lang, "continue"), callback_data="continue")
    return builder.as_markup()


def kb_tariffs(lang: str) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    for tariff in TARIFFS:
        name = lang_name(tariff, lang)
        price = short_price(tariff)
        builder.button(
            text=f"{name}  ·  {price}",
            callback_data=f"tariff:{tariff['id']}",
        )
    builder.adjust(1)
    return builder.as_markup()


def kb_tariff_detail(lang: str, tariff_id: str) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(text=t(lang, "pay_btn"), callback_data=f"pay:{tariff_id}")
    builder.button(text=t(lang, "back"), callback_data="back_to_tariffs")
    builder.adjust(1)
    return builder.as_markup()


def kb_payment_info(lang: str, tariff_id: str) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(text=t(lang, "copy_btn"), copy_text=CopyTextButton(text=PAYMENT_DETAILS))
    builder.button(text=t(lang, "paid_btn"), callback_data=f"paid:{tariff_id}")
    builder.button(text=t(lang, "back"), callback_data=f"back_to_tariff:{tariff_id}")
    builder.adjust(1)
    return builder.as_markup()


def kb_receipt_decision(payment_id: int) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(text=ADMIN_TEXTS["btn_approve"], callback_data=f"approve:{payment_id}")
    builder.button(text=ADMIN_TEXTS["btn_reject"], callback_data=f"reject:{payment_id}")
    builder.adjust(2)
    return builder.as_markup()


def kb_back_start(lang: str) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(text="🏠 /start", callback_data="restart")
    return builder.as_markup()


# ==================== Команды ====================

@dp.message(CommandStart())
async def cmd_start(message: Message) -> None:
    await db.upsert_user(message.from_user.id, message.from_user.username, message.from_user.full_name)
    lang = await db.get_lang(message.from_user.id)

    if STICKER_FILE_ID:
        try:
            await message.answer_sticker(sticker=STICKER_FILE_ID)
        except TelegramBadRequest as e:
            log.warning("Не удалось отправить стикер (проверьте STICKER_FILE_ID): %s", e)

    await message.answer(t(lang, "welcome"))
    await message.answer(t(lang, "choose_lang"), reply_markup=kb_language(lang))


@dp.message(Command("id"))
async def cmd_id(message: Message) -> None:
    await db.upsert_user(message.from_user.id, message.from_user.username, message.from_user.full_name)
    lang = await db.get_lang(message.from_user.id)
    await message.answer(t(lang, "my_id", user_id=message.from_user.id))


@dp.message(Command("help"))
async def cmd_help(message: Message) -> None:
    await db.upsert_user(message.from_user.id, message.from_user.username, message.from_user.full_name)
    lang = await db.get_lang(message.from_user.id)
    await message.answer(t(lang, "help"))


@dp.message(Command("profile"))
async def cmd_profile(message: Message) -> None:
    user_id = message.from_user.id
    await db.upsert_user(user_id, message.from_user.username, message.from_user.full_name)
    lang = await db.get_lang(user_id)

    active = await db.get_active_payment(user_id)
    if active:
        tariff = TARIFFS_BY_ID.get(active["tariff_id"])
        tariff_name = lang_name(tariff, lang) if tariff else active["tariff_id"]
        text = t(lang, "profile_active",
                 user_id=user_id,
                 tariff=tariff_name,
                 expires=active["expires_at"][:10])
    else:
        text = t(lang, "profile_inactive", user_id=user_id)
    await message.answer(text, reply_markup=kb_back_start(lang))


@dp.message(Command("admin"))
async def cmd_admin(message: Message) -> None:
    if not is_admin(message.from_user.id):
        await message.answer(ADMIN_TEXTS["denied"])
        return
    await message.answer(await admin_stats_text())


async def admin_stats_text() -> str:
    stats = await db.payment_stats()
    lines = [
        ADMIN_TEXTS["admin_header"],
        f"👥 <b>Юзеров:</b> {await db.count_users()}",
        f"💰 <b>Платежей:</b> {stats['total']}",
        f"   ✅ Одобрено: {stats['approved']}",
        f"   ❌ Отклонено: {stats['rejected']}",
        f"   ⏳ Ожидает: {stats['pending']}",
    ]

    by_tariff = await db.count_approved_by_tariff()
    if by_tariff:
        lines.append("\n━━━━━━━━━━━━━━━━━━━━")
        lines.append("📦 <b>По тарифам:</b>")
        for tf in TARIFFS:
            count = by_tariff.get(tf["id"], 0)
            if count:
                lines.append(f"   {tf['emoji']} {lang_name(tf, 'ru')}: <b>{count}</b>")

    active = await db.list_active_subscriptions()
    lines.append(f"\n━━━━━━━━━━━━━━━━━━━━")
    lines.append(f"🟢 <b>Активные подписки:</b> {len(active)}")
    for row in active[:20]:
        username = f" @{row['username']}" if row["username"] else ""
        tariff = TARIFFS_BY_ID.get(row["tariff_id"])
        tariff_name = lang_name(tariff, "ru") if tariff else row["tariff_id"]
        lines.append(f"  • <code>{row['user_id']}</code>{username} — {tariff_name} — до {row['expires_at'][:10]}")

    recent = await db.recent_payments(10)
    if recent:
        lines.append("\n━━━━━━━━━━━━━━━━━━━━")
        lines.append("🧾 <b>Последние платежи:</b>")
        for row in recent:
            username = f" @{row['username']}" if row["username"] else ""
            tariff = TARIFFS_BY_ID.get(row["tariff_id"])
            tariff_name = lang_name(tariff, "ru") if tariff else row["tariff_id"]
            emoji = STATUS_EMOJI.get(row["status"], "")
            lines.append(
                f"  {emoji} #{row['id']} <code>{row['user_id']}</code>{username}\n"
                f"     {tariff_name} — {row['created_at'][:16]}"
            )

    text = "\n".join(lines)
    return text if len(text) <= 4000 else text[:4000] + "…"


# ==================== Флоу юзера ====================

@dp.callback_query(F.data == "noop")
async def on_noop(call: CallbackQuery) -> None:
    """Пустая кнопка — текущий язык, ничего не делать."""
    await call.answer()


@dp.callback_query(F.data == "restart")
async def on_restart(call: CallbackQuery) -> None:
    """Кнопка «🏠 /start» — начать заново."""
    lang = await db.get_lang(call.from_user.id)
    await call.message.answer(t(lang, "welcome"))
    await call.message.answer(t(lang, "choose_lang"), reply_markup=kb_language(lang))
    await call.answer()


@dp.callback_query(F.data == "switch_lang")
async def switch_language(call: CallbackQuery) -> None:
    """Переключение языка RU <-> EN."""
    user_id = call.from_user.id
    await db.upsert_user(user_id, call.from_user.username, call.from_user.full_name)
    current = await db.get_lang(user_id)
    new_lang = "en" if current == "ru" else "ru"
    await db.set_lang(user_id, new_lang)

    await safe_edit(call.message, t(new_lang, "choose_lang"), kb_language(new_lang))
    await call.message.answer("👇", reply_markup=kb_continue(new_lang))
    await call.answer()


@dp.callback_query(F.data == "continue")
async def on_continue(call: CallbackQuery) -> None:
    lang = await db.get_lang(call.from_user.id)
    await safe_edit(call.message, t(lang, "tariff_intro"), kb_tariffs(lang))
    await call.answer()


@dp.callback_query(F.data.startswith("tariff:"))
async def on_tariff(call: CallbackQuery) -> None:
    tariff = TARIFFS_BY_ID.get(call.data.split(":", 1)[1])
    if tariff is None:
        await call.answer()
        return
    lang = await db.get_lang(call.from_user.id)
    text = t(
        lang,
        "tariff_detail",
        name=lang_name(tariff, lang),
        price=format_price(tariff),
        duration=lang_duration(tariff, lang),
        emoji=tariff["emoji"],
        desc=lang_desc(tariff, lang),
    )
    await safe_edit(call.message, text, kb_tariff_detail(lang, tariff["id"]))
    await call.answer()


@dp.callback_query(F.data == "back_to_tariffs")
async def back_to_tariffs(call: CallbackQuery) -> None:
    lang = await db.get_lang(call.from_user.id)
    await safe_edit(call.message, t(lang, "tariff_intro"), kb_tariffs(lang))
    await call.answer()


@dp.callback_query(F.data.startswith("pay:"))
async def on_pay(call: CallbackQuery) -> None:
    tariff = TARIFFS_BY_ID.get(call.data.split(":", 1)[1])
    if tariff is None:
        await call.answer()
        return
    user_id = call.from_user.id
    lang = await db.get_lang(user_id)
    text = t(
        lang,
        "payment_info",
        method=lang_method(lang),
        amount=format_price(tariff),
        user_id=user_id,
        details=PAYMENT_DETAILS,
    )
    await safe_edit(call.message, text, kb_payment_info(lang, tariff["id"]))
    await call.answer()


@dp.callback_query(F.data.startswith("paid:"))
async def on_paid(call: CallbackQuery) -> None:
    """«Я ОПЛАТИЛ» — переключаемся в режим ожидания квитанции."""
    tariff = TARIFFS_BY_ID.get(call.data.split(":", 1)[1])
    if tariff is None:
        await call.answer()
        return
    user_id = call.from_user.id
    await db.upsert_user(user_id, call.from_user.username, call.from_user.full_name)
    await db.set_awaiting(user_id, tariff["id"])
    lang = await db.get_lang(user_id)
    await safe_edit(call.message, t(lang, "receipt_request"))
    await call.answer()


@dp.callback_query(F.data.startswith("back_to_tariff:"))
async def back_to_tariff(call: CallbackQuery) -> None:
    tariff = TARIFFS_BY_ID.get(call.data.split(":", 1)[1])
    if tariff is None:
        await call.answer()
        return
    lang = await db.get_lang(call.from_user.id)
    text = t(
        lang,
        "tariff_detail",
        name=lang_name(tariff, lang),
        price=format_price(tariff),
        duration=lang_duration(tariff, lang),
        emoji=tariff["emoji"],
        desc=lang_desc(tariff, lang),
    )
    await safe_edit(call.message, text, kb_tariff_detail(lang, tariff["id"]))
    await call.answer()


# ==================== Квитанции ====================

@dp.message(F.photo)
async def handle_receipt(message: Message, bot: Bot) -> None:
    user_id = message.from_user.id
    await db.upsert_user(user_id, message.from_user.username, message.from_user.full_name)

    tariff_id = await db.get_awaiting(user_id)
    lang = await db.get_lang(user_id)
    tariff = TARIFFS_BY_ID.get(tariff_id) if tariff_id else None
    if tariff is None:
        # фото не по делу (не ждём квитанцию)
        await message.answer(t(lang, "unknown"))
        return

    # Каждое фото в режиме ожидания = новая квитанция (можно прислать несколько)
    payment_id = await db.create_pending_payment(user_id, tariff["id"], format_price(tariff))
    await db.attach_receipt(payment_id, message.photo[-1].file_id)
    await notify_admins_receipt(bot, message, payment_id, tariff)
    await message.answer(t(lang, "receipt_sent"))


async def notify_admins_receipt(bot: Bot, message: Message, payment_id: int, tariff: dict) -> None:
    """Пересылка квитанции всем админам с кнопками решения."""
    user = message.from_user
    username = ADMIN_TEXTS["username_fmt"].format(username=user.username, user_id=user.id) if user.username else ""
    active = await db.get_active_payment(user.id)
    active_note = ""
    if active:
        active_note = ADMIN_TEXTS["active_note_fmt"].format(expires=active["expires_at"][:10])

    caption = ADMIN_TEXTS["new_receipt_caption"].format(
        payment_id=payment_id,
        full_name=user.full_name,
        username=username,
        user_id=user.id,
        tariff=lang_name(tariff, "ru"),
        amount=format_price(tariff),
        sent_at=datetime.now().strftime("%d.%m.%Y %H:%M"),
        active_note=active_note,
    )

    for admin_id in ADMIN_IDS:
        try:
            await bot.send_photo(
                admin_id,
                photo=message.photo[-1].file_id,
                caption=caption,
                reply_markup=kb_receipt_decision(payment_id),
            )
        except Exception:
            log.exception("Не удалось отправить квитанцию админу %s", admin_id)


def _parse_payment_id(data: str) -> int | None:
    try:
        return int(data.split(":", 1)[1])
    except (IndexError, ValueError):
        return None


async def _edit_admin_mark(call: CallbackQuery, mark: str) -> None:
    """Пометить решение на сообщении с квитанцией (у сообщения есть фото — caption)."""
    try:
        base_caption = call.message.caption or ""
        await call.message.edit_caption(caption=base_caption + mark, reply_markup=None)
    except TelegramBadRequest as e:
        log.warning("Не удалось пометить сообщение админа: %s", e)


@dp.callback_query(F.data.startswith("approve:"))
async def on_approve(call: CallbackQuery, bot: Bot) -> None:
    if not is_admin(call.from_user.id):
        await call.answer(ADMIN_TEXTS["denied"], show_alert=True)
        return
    payment_id = _parse_payment_id(call.data)
    payment = await db.get_payment(payment_id) if payment_id else None
    if not payment or payment["status"] != "pending":
        await call.answer(ADMIN_TEXTS["already_processed"], show_alert=True)
        return

    tariff = TARIFFS_BY_ID.get(payment["tariff_id"])
    days = tariff["days"] if tariff else 30
    expires = db.expires_str(days)
    await db.set_payment_status(payment_id, "approved", expires)
    await db.set_awaiting(payment["user_id"], None)

    mark = ADMIN_TEXTS["approved_mark"].format(
        time=datetime.now().strftime("%d.%m.%Y %H:%M"), expires=expires[:10]
    )
    await _edit_admin_mark(call, mark)

    try:
        user_lang = await db.get_lang(payment["user_id"])
        await bot.send_message(payment["user_id"], t(user_lang, "payment_approved"))
    except Exception:
        log.exception("Не удалось уведомить юзера %s о подтверждении", payment["user_id"])

    await call.answer(ADMIN_TEXTS["approved_done"])


@dp.callback_query(F.data.startswith("reject:"))
async def on_reject(call: CallbackQuery, bot: Bot) -> None:
    if not is_admin(call.from_user.id):
        await call.answer(ADMIN_TEXTS["denied"], show_alert=True)
        return
    payment_id = _parse_payment_id(call.data)
    payment = await db.get_payment(payment_id) if payment_id else None
    if not payment or payment["status"] != "pending":
        await call.answer(ADMIN_TEXTS["already_processed"], show_alert=True)
        return

    await db.set_payment_status(payment_id, "rejected")
    # флаг ожидания НЕ снимаем: юзер может прислать другую квитанцию

    mark = ADMIN_TEXTS["rejected_mark"].format(time=datetime.now().strftime("%d.%m.%Y %H:%M"))
    await _edit_admin_mark(call, mark)

    try:
        user_lang = await db.get_lang(payment["user_id"])
        await bot.send_message(payment["user_id"], t(user_lang, "payment_rejected"))
    except Exception:
        log.exception("Не удалось уведомить юзера %s об отклонении", payment["user_id"])

    await call.answer(ADMIN_TEXTS["rejected_done"])


# ==================== Хелперы админа / фолбэки ====================

@dp.message(F.sticker)
async def admin_sticker_helper(message: Message) -> None:
    """Пересланный админом стикер -> отдаём его file_id для STICKER_FILE_ID."""
    if not is_admin(message.from_user.id):
        return  # чужие стикеры молча игнорируем
    await message.answer(
        ADMIN_TEXTS["sticker_hint"].format(file_id=message.sticker.file_id),
    )


@dp.message(F.document)
async def handle_document(message: Message) -> None:
    user_id = message.from_user.id
    await db.upsert_user(user_id, message.from_user.username, message.from_user.full_name)
    lang = await db.get_lang(user_id)
    if await db.get_awaiting(user_id):
        await message.answer(t(lang, "need_photo"))
    else:
        await message.answer(t(lang, "unknown"))


@dp.message(F.text)
async def text_fallback(message: Message) -> None:
    """Любой остальной текст (команды перехвачены выше)."""
    lang = await db.get_lang(message.from_user.id)
    await message.answer(t(lang, "unknown"))


# ==================== Ошибки и запуск ====================

@dp.error
async def on_error(event) -> None:
    log.exception("Необработанная ошибка: %s", event.exception)


async def main() -> None:
    if not BOT_TOKEN:
        raise SystemExit("❌ BOT_TOKEN не задан — заполните BOT_TOKEN в config.py")
    if not ADMIN_IDS:
        log.warning("ADMIN_IDS не заданы — квитанции некому пересылать! Заполните в config.py")

    await db.init_db()
    bot = Bot(token=BOT_TOKEN, default=DefaultBotProperties(parse_mode="HTML"))
    log.info("Бот запущен. Админы: %s", ADMIN_IDS or "не заданы")
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
