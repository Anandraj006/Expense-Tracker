from datetime import date

from Confi import MAX_AMOUNT, PAYMENT_METHODS
from Database import fetch_all, get_cursor


def _clean_date(value):
    try:
        return date.fromisoformat(str(value).strip()).isoformat()
    except ValueError:
        raise ValueError("Invalid date, use YYYY-MM-DD")


def _clean_amount(value):
    if not 0 < value <= MAX_AMOUNT:
        raise ValueError(f"Amount must be greater than 0 and at most {MAX_AMOUNT:,.2f}")
    return round(value, 2)


def _clean_method(value):
    value = (value or "cash").strip().lower() or "cash"
    if value not in PAYMENT_METHODS:
        raise ValueError("Payment method must be one of: " + ", ".join(PAYMENT_METHODS))
    return value


def _get_category(cur, user_id, category_id):
    cur.execute(
        "SELECT id, type FROM categories WHERE id = %s AND user_id = %s",
        (category_id, user_id),
    )
    return cur.fetchone()


def add_transaction(user_id, category_id, amount, ttype, tdate=None,
                    note="", payment_method="cash"):
    if ttype not in ("income", "expense"):
        raise ValueError("Type must be income or expense")
    amount = _clean_amount(amount)
    tdate = _clean_date(tdate) if tdate else date.today().isoformat()
    payment_method = _clean_method(payment_method)
    note = (note or "")[:255]

    with get_cursor() as cur:
        category = _get_category(cur, user_id, category_id)
        if not category:
            raise ValueError("Invalid category")
        if category["type"] != ttype:
            raise ValueError("Category type does not match the transaction type")
        cur.execute(
            """INSERT INTO transactions
               (user_id, category_id, amount, type, date, note, payment_method)
               VALUES (%s, %s, %s, %s, %s, %s, %s)""",
            (user_id, category_id, amount, ttype, tdate, note, payment_method),
        )
        return cur.lastrowid


def update_transaction(user_id, txn_id, **fields):
    allowed = {"category_id", "amount", "type", "date", "note", "payment_method"}
    updates = {k: v for k, v in fields.items() if k in allowed}
    if not updates:
        return False

    if "amount" in updates:
        updates["amount"] = _clean_amount(updates["amount"])
    if "date" in updates:
        updates["date"] = _clean_date(updates["date"])
    if "note" in updates:
        updates["note"] = (updates["note"] or "")[:255]
    if "payment_method" in updates:
        updates["payment_method"] = _clean_method(updates["payment_method"])
    if "type" in updates and updates["type"] not in ("income", "expense"):
        raise ValueError("Type must be income or expense")

    with get_cursor() as cur:
        cur.execute(
            "SELECT category_id, type FROM transactions WHERE id = %s AND user_id = %s",
            (txn_id, user_id),
        )
        current = cur.fetchone()
        if not current:
            return False

        if "category_id" in updates or "type" in updates:
            new_cat = updates.get("category_id", current["category_id"])
            new_type = updates.get("type", current["type"])
            category = _get_category(cur, user_id, new_cat)
            if not category:
                raise ValueError("Invalid category")
            if category["type"] != new_type:
                raise ValueError("Category type does not match the transaction type")

        set_clause = ", ".join(f"`{k}` = %s" for k in updates)
        cur.execute(
            f"UPDATE transactions SET {set_clause} WHERE id = %s AND user_id = %s",
            [*updates.values(), txn_id, user_id],
        )
        return cur.rowcount > 0


def delete_transaction(user_id, txn_id):
    with get_cursor() as cur:
        cur.execute(
            "DELETE FROM transactions WHERE id = %s AND user_id = %s",
            (txn_id, user_id),
        )
        return cur.rowcount > 0


def list_transactions(user_id, start=None, end=None, category_id=None,
                      ttype=None, min_amount=None, max_amount=None, search=None):
    if start:
        start = _clean_date(start)
    if end:
        end = _clean_date(end)

    query = """
        SELECT t.id, t.user_id, t.category_id, t.amount, t.type, t.date,
               t.note, t.payment_method, c.name AS category_name
        FROM transactions t JOIN categories c ON c.id = t.category_id
        WHERE t.user_id = %s
    """
    params = [user_id]
    if start:
        query += " AND t.date >= %s"
        params.append(start)
    if end:
        query += " AND t.date <= %s"
        params.append(end)
    if category_id:
        query += " AND t.category_id = %s"
        params.append(category_id)
    if ttype:
        query += " AND t.type = %s"
        params.append(ttype)
    if min_amount is not None:
        query += " AND t.amount >= %s"
        params.append(min_amount)
    if max_amount is not None:
        query += " AND t.amount <= %s"
        params.append(max_amount)
    if search:
        escaped = search.replace("\\", "\\\\").replace("%", "\\%").replace("_", "\\_")
        query += " AND t.note LIKE %s"
        params.append(f"%{escaped}%")
    query += " ORDER BY t.date DESC, t.id DESC"

    with get_cursor() as cur:
        cur.execute(query, params)
        return fetch_all(cur)