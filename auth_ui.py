from getpass import getpass

from auth import login_user, register_user


def read_username():
    while True:
        username = input("Enter username: ").strip()
        if not 3 <= len(username) <= 50:
            print("Username must be 3 to 50 characters.")
            continue
        if " " in username:
            print("Username cannot contain spaces.")
            continue
        return username


def read_password(confirm=False):
    while True:
        password = getpass("Enter password: ")
        if len(password) < 6:
            print("Password must be at least 6 characters.")
            continue
        if confirm:
            again = getpass("Confirm password: ")
            if password != again:
                print("Passwords do not match. Try again.")
                continue
        return password


def register():
    print("\n--- Register ---")
    username = read_username()
    password = read_password(confirm=True)
    try:
        user_id = register_user(username, password)
        print("Registration successful.")
        return user_id
    except ValueError as e:
        print(f"Error: {e}")
        return None


def login():
    print("\n--- Login ---")
    for attempt in range(3):
        username = input("Enter username: ").strip()
        password = getpass("Enter password: ")
        user_id = login_user(username, password)
        if user_id:
            print(f"Welcome, {username}!")
            return user_id
        print(f"Invalid username or password. Attempts left: {2 - attempt}")
    print("Too many failed attempts.")
    return None


def start_menu():
    while True:
        print("\n===== Welcome =====")
        print("1. Register")
        print("2. Login")
        print("3. Exit")
        choice = input("Choose: ").strip()

        match choice:
            case "1":
                if register():
                    user_id = login()
                    if user_id:
                        return user_id
            case "2":
                user_id = login()
                if user_id:
                    return user_id
            case "3":
                return None
            case _:
                print("Invalid choice.")