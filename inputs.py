import math
from datetime import date

from categories import list_categories


def read_text(prompt, allow_empty=False):
    while True:
        value = input(prompt).strip()
        if value or allow_empty:
            return value
        print("This field cannot be empty.")


def read_float(prompt, minimum=0.01):
    while True:
        try:
            value = float(input(prompt).strip())
        except ValueError:
            print("Enter a valid number.")
            continue
        if not math.isfinite(value):
            print("Enter a valid number.")
            continue
        if value < minimum:
            print(f"Value must be at least {minimum}.")
            continue
        return value


def read_int(prompt, low, high):
    while True:
        try:
            value = int(input(prompt).strip())
            if low <= value <= high:
                return value
            print(f"Enter a number between {low} and {high}.")
        except ValueError:
            print("Enter a valid whole number.")


def read_date(prompt):
    while True:
        value = input(f"{prompt} (YYYY-MM-DD, Enter for today): ").strip()
        if not value:
            return date.today().isoformat()
        try:
            return date.fromisoformat(value).isoformat()
        except ValueError:
            print("Invalid date format.")


def read_type():
    while True:
        value = input("Type (income/expense): ").strip().lower()
        if value in ("income", "expense"):
            return value
        print("Enter 'income' or 'expense'.")


def read_month_year():
    today = date.today()
    raw_m = input(f"Month 1-12 (Enter for {today.month}): ").strip()
    raw_y = input(f"Year 2000-2100 (Enter for {today.year}): ").strip()
    month = int(raw_m) if raw_m.isdigit() and 1 <= int(raw_m) <= 12 else today.month
    year = int(raw_y) if raw_y.isdigit() and 2000 <= int(raw_y) <= 2100 else today.year
    return month, year


def pick_category(user_id, ctype):
    categories = list_categories(user_id, ctype)
    if not categories:
        print("No categories found.")
        return None
    print("\nCategories:")
    for i, c in enumerate(categories, 1):
        print(f"  {i}. {c['name']}")
    choice = read_int("Choose category number: ", 1, len(categories))
    return categories[choice - 1]["id"]


def print_transactions(rows):
    if not rows:
        print("No transactions found.")
        return
    print(f"\n{'ID':<5}{'Date':<12}{'Category':<16}{'Type':<9}{'Amount':>10}  Note")
    print("-" * 70)
    for r in rows:
        print(f"{r['id']:<5}{r['date']:<12}{r['category_name']:<16}"
              f"{r['type']:<9}{r['amount']:>10.2f}  {r['note']}")