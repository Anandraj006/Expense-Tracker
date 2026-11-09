import csv

from transactions import list_transactions


def export_transactions_csv(user_id, filepath, **filters):
    rows = list_transactions(user_id, **filters)
    with open(filepath, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["Date", "Category", "Type", "Amount", "Payment Method", "Note"])
        for r in rows:
            writer.writerow([
                r["date"], r["category_name"], r["type"],
                r["amount"], r["payment_method"], r["note"],
            ])
    return len(rows)