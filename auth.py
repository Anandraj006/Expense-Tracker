import hashlib
import hmac
import os

from mysql.connector import IntegrityError

from Confi import DEFAULT_CATEGORIES
from Database import get_cursor


def _hash_password(password, salt):
    return hashlib.pbkdf2_hmac(
        "sha256", password.encode(), bytes.fromhex(salt), 200_000
    ).hex()


def register_user(username, password):
    username = username.strip()
    if not 3 <= len(username) <= 50:
        raise ValueError("Username must be 3 to 50 characters")
    if " " in username:
        raise ValueError("Username cannot contain spaces")
    if len(password) < 6:
        raise ValueError("Password must be at least 6 characters")

    salt = os.urandom(16).hex()
    pw_hash = _hash_password(password, salt)

    # User and default categories are saved in ONE transaction:
    # if anything fails, nothing is saved.
    with get_cursor() as cur:
        try:
            cur.execute(
                "INSERT INTO users (username, password_hash, salt) VALUES (%s, %s, %s)",
                (username, pw_hash, salt),
            )
        except IntegrityError:
            raise ValueError("Username already taken")
        user_id = cur.lastrowid
        rows = [
            (user_id, name, ctype)
            for ctype, names in DEFAULT_CATEGORIES.items()
            for name in names
        ]
        cur.executemany(
            "INSERT INTO categories (user_id, name, type) VALUES (%s, %s, %s)",
            rows,
        )
    return user_id


def login_user(username, password):
    with get_cursor() as cur:
        cur.execute(
            "SELECT id, password_hash, salt FROM users WHERE username = %s",
            (username.strip(),),
        )
        row = cur.fetchone()

    if row is None:
        _hash_password(password, "00" * 16)  # same work, so timing does not reveal valid usernames
        return None

    attempt = _hash_password(password, row["salt"])
    if hmac.compare_digest(attempt, row["password_hash"]):
        return row["id"]
    return None