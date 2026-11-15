"""SQLite-хранилище бота (aiosqlite).

База лежит в bot.db рядом с кодом. Таблицы:
- users    — профиль, язык и флаг «ожидаем квитанцию» (awaiting_tariff)
- payments — история платежей/квитанций (pending -> approved | rejected)
"""
from datetime import datetime, timedelta
from pathlib import Path

import aiosqlite

DB_PATH = Path(__file__).resolve().parent / "bot.db"

DATE_FMT = "%Y-%m-%d %H:%M:%S"


def now_str() -> str:
    return datetime.now().strftime(DATE_FMT)


def expires_str(days: int) -> str:
    return (datetime.now() + timedelta(days=days)).strftime(DATE_FMT)


async def _fetch(query: str, params: tuple = ()) -> list:
    async with aiosqlite.connect(DB_PATH) as conn:
        conn.row_factory = aiosqlite.Row
        async with conn.execute(query, params) as cur:
            return list(await cur.fetchall())


async def _execute(query: str, params: tuple = ()) -> int:
    """Выполнить запрос, вернуть lastrowid."""
    async with aiosqlite.connect(DB_PATH) as conn:
        cur = await conn.execute(query, params)
        await conn.commit()
        return cur.lastrowid


async def init_db() -> None:
    async with aiosqlite.connect(DB_PATH) as conn:
        await conn.execute(
            """
            CREATE TABLE IF NOT EXISTS users (
                user_id         INTEGER PRIMARY KEY,
                username        TEXT,
                full_name       TEXT,
                lang            TEXT NOT NULL DEFAULT 'ru',
                awaiting_tariff TEXT,
                created_at      TEXT NOT NULL
            )
            """
        )
        await conn.execute(
            """
            CREATE TABLE IF NOT EXISTS payments (
                id              INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id         INTEGER NOT NULL,
                tariff_id       TEXT NOT NULL,
                amount          TEXT NOT NULL,
                status          TEXT NOT NULL DEFAULT 'pending',
                receipt_file_id TEXT,
                created_at      TEXT NOT NULL,
                decided_at      TEXT,
                expires_at      TEXT
            )
            """
        )
        await conn.execute(
            "CREATE INDEX IF NOT EXISTS idx_payments_user ON payments(user_id, status)"
        )
        await conn.commit()


# ==================== Пользователи ====================

async def upsert_user(user_id: int, username: str | None, full_name: str) -> None:
    """Создать юзера (язык по умолчанию ru) или обновить его профиль.

    Язык здесь не трогаем — им управляет set_lang.
    """
    await _execute(
        """
        INSERT INTO users (user_id, username, full_name, created_at)
        VALUES (?, ?, ?, ?)
        ON CONFLICT(user_id) DO UPDATE SET
            username = excluded.username,
            full_name = excluded.full_name
        """,
        (user_id, username, full_name, now_str()),
    )


async def set_lang(user_id: int, lang: str) -> None:
    await _execute(
        """
        INSERT INTO users (user_id, lang, created_at) VALUES (?, ?, ?)
        ON CONFLICT(user_id) DO UPDATE SET lang = excluded.lang
        """,
        (user_id, lang, now_str()),
    )


async def get_lang(user_id: int) -> str:
    rows = await _fetch("SELECT lang FROM users WHERE user_id = ?", (user_id,))
    return rows[0]["lang"] if rows else "ru"


async def set_awaiting(user_id: int, tariff_id: str | None) -> None:
    """Пометить, что ждём квитанцию по тарифу (None — снять флаг)."""
    await _execute("UPDATE users SET awaiting_tariff = ? WHERE user_id = ?", (tariff_id, user_id))


async def get_awaiting(user_id: int) -> str | None:
    rows = await _fetch("SELECT awaiting_tariff FROM users WHERE user_id = ?", (user_id,))
    return rows[0]["awaiting_tariff"] if rows else None


async def count_users() -> int:
    rows = await _fetch("SELECT COUNT(*) AS c FROM users")
    return rows[0]["c"]


# ==================== Платежи ====================

async def create_pending_payment(user_id: int, tariff_id: str, amount: str) -> int:
    return await _execute(
        """
        INSERT INTO payments (user_id, tariff_id, amount, status, created_at)
        VALUES (?, ?, ?, 'pending', ?)
        """,
        (user_id, tariff_id, amount, now_str()),
    )


async def attach_receipt(payment_id: int, file_id: str) -> None:
    await _execute("UPDATE payments SET receipt_file_id = ? WHERE id = ?", (file_id, payment_id))


async def set_payment_status(payment_id: int, status: str, expires_at: str | None = None) -> None:
    await _execute(
        "UPDATE payments SET status = ?, decided_at = ?, expires_at = ? WHERE id = ?",
        (status, now_str(), expires_at, payment_id),
    )


async def get_payment(payment_id: int) -> dict | None:
    rows = await _fetch("SELECT * FROM payments WHERE id = ?", (payment_id,))
    return dict(rows[0]) if rows else None


async def get_latest_pending_for(user_id: int, tariff_id: str) -> dict | None:
    rows = await _fetch(
        """
        SELECT * FROM payments
        WHERE user_id = ? AND tariff_id = ? AND status = 'pending'
        ORDER BY id DESC LIMIT 1
        """,
        (user_id, tariff_id),
    )
    return dict(rows[0]) if rows else None


async def get_active_payment(user_id: int) -> dict | None:
    """Последний одобренный платёж с неистёкшим сроком."""
    rows = await _fetch(
        """
        SELECT * FROM payments
        WHERE user_id = ? AND status = 'approved' AND expires_at > ?
        ORDER BY id DESC LIMIT 1
        """,
        (user_id, now_str()),
    )
    return dict(rows[0]) if rows else None


# ==================== Статистика для /admin ====================

async def payment_stats() -> dict:
    rows = await _fetch("SELECT status, COUNT(*) AS c FROM payments GROUP BY status")
    by_status = {r["status"]: r["c"] for r in rows}
    total = sum(by_status.values())
    return {
        "total": total,
        "approved": by_status.get("approved", 0),
        "rejected": by_status.get("rejected", 0),
        "pending": by_status.get("pending", 0),
    }


async def count_approved_by_tariff() -> dict[str, int]:
    rows = await _fetch(
        "SELECT tariff_id, COUNT(*) AS c FROM payments WHERE status = 'approved' GROUP BY tariff_id"
    )
    return {r["tariff_id"]: r["c"] for r in rows}


async def list_active_subscriptions() -> list[dict]:
    """Активные подписки: последняя одобренная каждого юзера с неистёкшим сроком."""
    rows = await _fetch(
        """
        SELECT p.*, u.username, u.full_name
        FROM payments p
        JOIN users u ON u.user_id = p.user_id
        WHERE p.status = 'approved' AND p.expires_at > ?
          AND p.id = (
              SELECT MAX(p2.id) FROM payments p2
              WHERE p2.user_id = p.user_id AND p2.status = 'approved' AND p2.expires_at > ?
          )
        ORDER BY p.expires_at
        """,
        (now_str(), now_str()),
    )
    return [dict(r) for r in rows]


async def recent_payments(limit: int = 10) -> list[dict]:
    rows = await _fetch(
        """
        SELECT p.*, u.username, u.full_name
        FROM payments p
        LEFT JOIN users u ON u.user_id = p.user_id
        ORDER BY p.id DESC LIMIT ?
        """,
        (limit,),
    )
    return [dict(r) for r in rows]
