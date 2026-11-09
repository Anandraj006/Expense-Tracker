import mysql.connector

from auth_ui import start_menu
from Database import init_db
from menu_ui import main_menu


if __name__ == "__main__":
    try:
        init_db()
        current_user = start_menu()
        if current_user:
            main_menu(current_user)
    except mysql.connector.Error as e:
        print(f"\nDatabase error: {e}")
        print("Check that MySQL is running and the settings in config.py are correct.")
        raise SystemExit(1)
    print("Goodbye!")