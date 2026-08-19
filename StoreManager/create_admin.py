import getpass

from werkzeug.security import generate_password_hash

from backend.db import get_connection


def create_user():

    print("=" * 50)
    print("       STORE MANAGER - CREATE USER")
    print("=" * 50)

    print()
    print("Available roles:")
    print("1. Admin")
    print("2. Manager")
    print("3. Employee")
    print()

    role_choice = input(
        "Select role (1/2/3): "
    ).strip()

    roles = {
        "1": "Admin",
        "2": "Manager",
        "3": "Employee"
    }

    if role_choice not in roles:
        print("Invalid role selection.")
        return

    role = roles[role_choice]

    print()

    username = input(
        f"{role} username: "
    ).strip()

    if not username:
        print("Username cannot be empty.")
        return

    password = getpass.getpass(
        f"{role} password: "
    )

    if not password:
        print("Password cannot be empty.")
        return

    confirm_password = getpass.getpass(
        "Confirm password: "
    )

    if password != confirm_password:
        print("Passwords do not match.")
        return

    connection = None
    cursor = None

    try:

        connection = get_connection()
        cursor = connection.cursor()

        cursor.execute(
            """
            SELECT user_id
            FROM users
            WHERE username = %s
            LIMIT 1
            """,
            (username,)
        )

        if cursor.fetchone():

            print(
                f"Username '{username}' already exists."
            )

            return

        password_hash = generate_password_hash(
            password
        )

        cursor.execute(
            """
            INSERT INTO users
            (
                username,
                password,
                role
            )
            VALUES
            (
                %s,
                %s,
                %s
            )
            """,
            (
                username,
                password_hash,
                role
            )
        )

        connection.commit()

        print()
        print("=" * 50)
        print("User created successfully!")
        print("=" * 50)
        print(f"Username : {username}")
        print(f"Role     : {role}")

    except Exception as error:

        if connection:
            connection.rollback()

        print()
        print("Failed to create user.")
        print(f"Error: {error}")

    finally:

        if cursor:
            cursor.close()

        if connection:
            connection.close()


if __name__ == "__main__":
    create_user()