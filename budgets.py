from Confi import MAX_AMOUNT
from Database import fetch_all, get_cursor
from utils import month_range


def set_budget(user_id, category_id, month, year, limit_amount):
    if not 1 <= month <= 12:
        raise ValueError("Month must be between 1 and 12")
    if not 2000 <= year <= 2100:
        raise ValueError("Year must be between 2000 and 2100")
    if not 0 < limit_amount <= MAX_AMOUNT:
        raise ValueError(f"Limit must be greater than 0 and at most {MAX_AMOUNT:,.2f}")

    with get_cursor() as cur:
        cur.execute(
            "SELECT type FROM categories WHERE id = %s AND user_id = %s",
            (category_id, user_id),
        )
        category = cur.fetchone()
        if not category:
            raise ValueError("Invalid category")
        if category["type"] != "expense":
            raise ValueError("Budgets can only be set on expense categories")

        cur.execute(
            """INSERT INTO budgets (user_id, category_id, month, year, limit_amount)
               VALUES (%s, %s, %s, %s, %s)
               ON DUPLICATE KEY UPDATE limit_amount = VALUES(limit_amount)""",
            (user_id, category_id, month, year, round(limit_amount, 2)),
        )


def budget_status(user_id, month, year):
    start, end = month_range(month, year)
    with get_cursor() as cur:
        cur.execute(
            """
            SELECT c.name AS category, b.limit_amount,
                   COALESCE((
                       SELECT SUM(t.amount) FROM transactions t
                       WHERE t.user_id = b.user_id
                         AND t.category_id = b.category_id
                         AND t.type = 'expense'
                         AND t.date >= %s AND t.date < %s
                   ), 0) AS spent
            FROM budgets b JOIN categories c ON c.id = b.category_id
            WHERE b.user_id = %s AND b.month = %s AND b.year = %s
            ORDER BY c.name
            """,
            (start, end, user_id, month, year),
        )
        rows = fetch_all(cur)

    result = []
    for r in rows:
        pct = round(r["spent"] / r["limit_amount"] * 100, 1)
        if pct >= 100:
            status = "Over budget"
        elif pct >= 80:
            status = "Warning"
        else:
            status = "OK"
        result.append({
            "category": r["category"],
            "limit": r["limit_amount"],
            "spent": r["spent"],
            "remaining": round(r["limit_amount"] - r["spent"], 2),
            "percentage": pct,
            "status": status,
        })
    return result