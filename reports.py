from Database import fetch_all, get_cursor
from utils import month_range, year_range


def monthly_summary(user_id, month, year):
    start, end = month_range(month, year)
    with get_cursor() as cur:
        cur.execute(
            """SELECT type, COALESCE(SUM(amount), 0) AS total
               FROM transactions
               WHERE user_id = %s AND date >= %s AND date < %s
               GROUP BY type""",
            (user_id, start, end),
        )
        rows = fetch_all(cur)
    totals = {r["type"]: r["total"] for r in rows}
    income = totals.get("income", 0)
    expense = totals.get("expense", 0)
    return {
        "income": income,
        "expense": expense,
        "balance": round(income - expense, 2),
    }


def spending_by_category(user_id, month, year):
    start, end = month_range(month, year)
    with get_cursor() as cur:
        cur.execute(
            """SELECT c.name AS category, SUM(t.amount) AS total
               FROM transactions t JOIN categories c ON c.id = t.category_id
               WHERE t.user_id = %s AND t.type = 'expense'
                 AND t.date >= %s AND t.date < %s
               GROUP BY c.name
               ORDER BY total DESC""",
            (user_id, start, end),
        )
        return fetch_all(cur)


def income_vs_expense_by_month(user_id, year):
    start, end = year_range(year)
    with get_cursor() as cur:
        cur.execute(
            """SELECT MONTH(date) AS month, type, SUM(amount) AS total
               FROM transactions
               WHERE user_id = %s AND date >= %s AND date < %s
               GROUP BY MONTH(date), type
               ORDER BY month""",
            (user_id, start, end),
        )
        rows = fetch_all(cur)
    data = {f"{m:02d}": {"income": 0, "expense": 0} for m in range(1, 13)}
    for r in rows:
        data[f"{r['month']:02d}"][r["type"]] = r["total"]
    return data


def daily_spending_trend(user_id, month, year):
    start, end = month_range(month, year)
    with get_cursor() as cur:
        cur.execute(
            """SELECT date, SUM(amount) AS total
               FROM transactions
               WHERE user_id = %s AND type = 'expense'
                 AND date >= %s AND date < %s
               GROUP BY date
               ORDER BY date""",
            (user_id, start, end),
        )
        return fetch_all(cur)