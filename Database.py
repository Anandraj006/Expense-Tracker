from contextlib import contextmanager
from datetime import date
from decimal import Decimal

import mysql.connector as db
from mysql.connector.constants import ClientFlag

from Confi import DB_CONFIG ,DB_NAME

def _connect(with_db = True):
    cfg = dict(DB_CONFIG)
    cfg["client_flags"] = [ClientFlag.FOUND_ROWS]
    if with_db : 
        cfg["database"] = DB_NAME
    return db.connect(**cfg)

@contextmanager
def get_cursor():
    """One connection and one transaction per block.
    Commits on success, rolls back on any error."""
    conn = _connect()
    cur = conn.cursor(dictionary=True)
    try:
        yield cur
        conn.commit()
    except Exception:
        try:
            conn.rollback()
        except db.Error:
            pass
        raise
    finally:
        cur.close()
        conn.close()


def _clean(row):
    """Decimal -> float and date -> 'YYYY-MM-DD' text so the rest of the app
    works with plain values."""
    out = {}
    for key, value in row.items():
        if isinstance(value, Decimal):
            out[key] = float(value)
        elif isinstance(value, date):
            out[key] = value.isoformat()
        else:
            out[key] = value
    return out


def fetch_all(cur):
    return [_clean(r) for r in cur.fetchall()]


def fetch_one(cur):
    row = cur.fetchone()
    return _clean(row) if row else None


TABLES = [
    """
    CREATE TABLE IF NOT EXISTS users (
        id INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
        username VARCHAR(50) NOT NULL UNIQUE,
        password_hash CHAR(64) NOT NULL,
        salt CHAR(32) NOT NULL
    ) ENGINE=InnoDB
    """,
    """
    CREATE TABLE IF NOT EXISTS categories (
        id INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
        user_id INT UNSIGNED NOT NULL,
        name VARCHAR(50) NOT NULL,
        type ENUM('income','expense') NOT NULL,
        UNIQUE KEY uq_category (user_id, name, type),
        CONSTRAINT fk_cat_user FOREIGN KEY (user_id)
            REFERENCES users(id) ON DELETE CASCADE
    ) ENGINE=InnoDB
    """,
    """
    CREATE TABLE IF NOT EXISTS transactions (
        id INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
        user_id INT UNSIGNED NOT NULL,
        category_id INT UNSIGNED NOT NULL,
        amount DECIMAL(12,2) NOT NULL,
        type ENUM('income','expense') NOT NULL,
        date DATE NOT NULL,
        note VARCHAR(255) NOT NULL DEFAULT '',
        payment_method VARCHAR(10) NOT NULL DEFAULT 'cash',
        INDEX idx_user_date (user_id, date),
        CONSTRAINT chk_txn_amount CHECK (amount > 0),
        CONSTRAINT fk_txn_user FOREIGN KEY (user_id)
            REFERENCES users(id) ON DELETE CASCADE,
        CONSTRAINT fk_txn_cat FOREIGN KEY (category_id)
            REFERENCES categories(id)
    ) ENGINE=InnoDB
    """,
    """
    CREATE TABLE IF NOT EXISTS budgets (
        id INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
        user_id INT UNSIGNED NOT NULL,
        category_id INT UNSIGNED NOT NULL,
        month TINYINT UNSIGNED NOT NULL,
        year SMALLINT UNSIGNED NOT NULL,
        limit_amount DECIMAL(12,2) NOT NULL,
        UNIQUE KEY uq_budget (user_id, category_id, month, year),
        CONSTRAINT chk_budget_month CHECK (month BETWEEN 1 AND 12),
        CONSTRAINT chk_budget_limit CHECK (limit_amount > 0),
        CONSTRAINT fk_bud_user FOREIGN KEY (user_id)
            REFERENCES users(id) ON DELETE CASCADE,
        CONSTRAINT fk_bud_cat FOREIGN KEY (category_id)
            REFERENCES categories(id) ON DELETE CASCADE
    ) ENGINE=InnoDB
    """,
]


def init_db():
    # The MySQL user needs CREATE privilege for the first run.
    root = _connect(with_db=False)
    try:
        root_cur = root.cursor()
        root_cur.execute(
            f"CREATE DATABASE IF NOT EXISTS `{DB_NAME}` "
            "CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci"
        )
        root_cur.close()
        root.commit()
    finally:
        root.close()

    with get_cursor() as cur:
        for statement in TABLES:
            cur.execute(statement)


