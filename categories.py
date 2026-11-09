from mysql.connector import IntegrityError

from Database import fetch_all, get_cursor


def add_category(user_id, name, ctype):
    name = name.strip()
    if not 1 <= len(name) <= 50:
        raise ValueError("Category name must be 1 to 50 characters")
    if ctype not in ("income", "expense"):
        raise ValueError("Type must be income or expense")
    with get_cursor() as cur:
        try:
            cur.execute(
                "INSERT INTO categories (user_id, name, type) VALUES (%s, %s, %s)",
                (user_id, name, ctype),
            )
        except IntegrityError:
            raise ValueError("Category already exists")
        return cur.lastrowid


def list_categories(user_id, ctype=None):
    query = "SELECT id, user_id, name, type FROM categories WHERE user_id = %s"
    params = [user_id]
    if ctype:
        query += " AND type = %s"
        params.append(ctype)
    query += " ORDER BY name"
    with get_cursor() as cur:
        cur.execute(query, params)
        return fetch_all(cur)