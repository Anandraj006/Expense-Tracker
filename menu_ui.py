from datetime import date

from budgets import budget_status, set_budget
from categories import add_category
from exporter import export_transactions_csv
from inputs import (
    pick_category,
    print_transactions,
    read_date,
    read_float,
    read_int,
    read_month_year,
    read_text,
    read_type,
)
from reports import (
    daily_spending_trend,
    income_vs_expense_by_month,
    monthly_summary,
    spending_by_category,
)
from transactions import (
    add_transaction,
    delete_transaction,
    list_transactions,
    update_transaction,
)


def action_add_transaction(user_id):
    ttype = read_type()
    category_id = pick_category(user_id, ttype)
    if category_id is None:
        return
    amount = read_float("Amount: ")
    tdate = read_date("Date")
    note = read_text("Note (optional): ", allow_empty=True)
    method = input("Payment method (cash/card/upi/bank/other) [cash]: ").strip().lower() or "cash"
    try:
        txn_id = add_transaction(user_id, category_id, amount, ttype, tdate, note, method)
        print(f"Saved transaction #{txn_id}.")
    except ValueError as e:
        print(f"Error: {e}")


def action_view_transactions(user_id):
    print("\nFilters (press Enter to skip each one)")
    start_d = input("From date (YYYY-MM-DD): ").strip() or None
    end_d = input("To date (YYYY-MM-DD): ").strip() or None
    ttype = input("Type (income/expense): ").strip().lower() or None
    search = input("Search in note: ").strip() or None
    try:
        rows = list_transactions(user_id, start=start_d, end=end_d, ttype=ttype, search=search)
    except ValueError as e:
        print(f"Error: {e}")
        return
    print_transactions(rows)


def action_edit_transaction(user_id):
    print_transactions(list_transactions(user_id)[:15])
    txn_id = read_int("Transaction ID to edit: ", 1, 10**9)
    print("Leave a field empty to keep its current value.")
    updates = {}
    amount = input("New amount: ").strip()
    if amount:
        try:
            value = float(amount)
            if value > 0:
                updates["amount"] = value
            else:
                print("Amount must be greater than zero, skipped.")
        except ValueError:
            print("Invalid amount, skipped.")
    note = input("New note: ").strip()
    if note:
        updates["note"] = note
    new_date = input("New date (YYYY-MM-DD): ").strip()
    if new_date:
        try:
            updates["date"] = date.fromisoformat(new_date).isoformat()
        except ValueError:
            print("Invalid date, skipped.")
    try:
        if update_transaction(user_id, txn_id, **updates):
            print("Updated.")
        else:
            print("Nothing changed or ID not found.")
    except ValueError as e:
        print(f"Error: {e}")


def action_delete_transaction(user_id):
    print_transactions(list_transactions(user_id)[:15])
    txn_id = read_int("Transaction ID to delete: ", 1, 10**9)
    if input("Type 'yes' to confirm: ").strip().lower() == "yes":
        print("Deleted." if delete_transaction(user_id, txn_id) else "ID not found.")
    else:
        print("Cancelled.")


def action_add_category(user_id):
    name = read_text("Category name: ")
    ctype = read_type()
    try:
        add_category(user_id, name, ctype)
        print("Category added.")
    except ValueError as e:
        print(f"Error: {e}")


def action_set_budget(user_id):
    category_id = pick_category(user_id, "expense")
    if category_id is None:
        return
    month, year = read_month_year()
    limit = read_float("Monthly limit: ")
    try:
        set_budget(user_id, category_id, month, year, limit)
        print("Budget saved.")
    except ValueError as e:
        print(f"Error: {e}")


def action_budget_status(user_id):
    month, year = read_month_year()
    rows = budget_status(user_id, month, year)
    if not rows:
        print("No budgets set for this month.")
        return
    print(f"\n{'Category':<16}{'Limit':>10}{'Spent':>10}{'Left':>10}{'Used%':>8}  Status")
    print("-" * 64)
    for r in rows:
        print(f"{r['category']:<16}{r['limit']:>10.2f}{r['spent']:>10.2f}"
              f"{r['remaining']:>10.2f}{r['percentage']:>8}  {r['status']}")
        if r["status"] == "Over budget":
            print(f"  ALERT: {r['category']} budget exceeded!")
        elif r["status"] == "Warning":
            print(f"  WARNING: {r['category']} has used {r['percentage']}% of its budget.")


def action_summary(user_id):
    month, year = read_month_year()
    s = monthly_summary(user_id, month, year)
    print(f"\nSummary for {month:02d}/{year}")
    print(f"  Income : {s['income']:.2f}")
    print(f"  Expense: {s['expense']:.2f}")
    print(f"  Balance: {s['balance']:.2f}")


def action_reports(user_id):
    month, year = read_month_year()

    print("\nSpending by category")
    for r in spending_by_category(user_id, month, year):
        print(f"  {r['category']:<16}{r['total']:>10.2f}")

    print("\nIncome vs expense by month")
    for m, v in income_vs_expense_by_month(user_id, year).items():
        print(f"  {m}  income {v['income']:>10.2f}   expense {v['expense']:>10.2f}")

    print("\nDaily spending trend")
    for r in daily_spending_trend(user_id, month, year):
        print(f"  {r['date']}  {r['total']:>10.2f}")


def action_export(user_id):
    path = read_text("File name (e.g. transactions.csv): ")
    if not path.endswith(".csv"):
        path += ".csv"
    try:
        count = export_transactions_csv(user_id, path)
        print(f"Exported {count} transactions to {path}.")
    except OSError as e:
        print(f"Could not write the file: {e}")


MENU = """
===== Expense Tracker =====
1. Add transaction
2. View transactions
3. Edit transaction
4. Delete transaction
5. Add category
6. Set budget
7. Budget status
8. Monthly summary
9. Reports
10. Export CSV
0. Logout
"""


def main_menu(user_id):
    while True:
        print(MENU)
        choice = input("Choose: ").strip()

        match choice:
            case "1":
                action_add_transaction(user_id)
            case "2":
                action_view_transactions(user_id)
            case "3":
                action_edit_transaction(user_id)
            case "4":
                action_delete_transaction(user_id)
            case "5":
                action_add_category(user_id)
            case "6":
                action_set_budget(user_id)
            case "7":
                action_budget_status(user_id)
            case "8":
                action_summary(user_id)
            case "9":
                action_reports(user_id)
            case "10":
                action_export(user_id)
            case "0":
                print("Logged out.")
                break
            case _:
                print("Invalid choice. Try again.")