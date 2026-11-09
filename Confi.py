# config.py  (no os module, values are written directly)

DB_NAME = "Expense_tracker"

DB_CONFIG = {
    "host": "localhost",
    "port": 3306,
    "user": "root",
    "password": "60006",   # change this to your MySQL password
    "charset": "utf8mb4",
}

DEFAULT_CATEGORIES = {
    "expense": ["Food", "Transport", "Rent", "Shopping", "Bills", "Health", "Entertainment"],
    "income": ["Salary", "Other Income"],
}

PAYMENT_METHODS = ("cash", "card", "upi", "bank", "other")

MAX_AMOUNT = 9_999_999_999.99