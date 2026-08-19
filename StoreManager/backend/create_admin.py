import getpass

from werkzeug.security import generate_password_hash

from backend.db import get_connection


# =========================================================
# CREATE STORE MANAGER USER
# =========================================================

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


    # =====================================================
    # ROLE SELECTION
    # =====================================================

    role_map = {
        "1": "Admin",
        "2": "Manager",
        "3": "Employee"
    }


    if role_choice not in role_map:

        print()

        print(
            "Invalid role selection."
        )

        return


    role = role_map[role_choice]


    print()


    # =====================================================
    # USERNAME
    # =====================================================

    username = input(
        f"{role} username: "
    ).strip()


    if not username:

        print()

        print(
            "Username cannot be empty."
        )

        return


    # =====================================================
    # PASSWORD
    # =====================================================

    password = getpass.getpass(
        f"{role} password: "
    )


    if not password:

        print()

        print(
            "Password cannot be empty."
        )

        return


    # =====================================================
    # CONFIRM PASSWORD
    # =====================================================

    confirm_password = getpass.getpass(
        "Confirm password: "
    )


    if password != confirm_password:

        print()

        print(
            "Passwords do not match."
        )

        return


    connection = None
    cursor = None


    try:

        # =================================================
        # DATABASE CONNECTION
        # =================================================

        connection = get_connection()

        cursor = connection.cursor()


        # =================================================
        # CHECK WHETHER USER ALREADY EXISTS
        # =================================================

        cursor.execute(
            """
            SELECT user_id
            FROM users
            WHERE username = %s
            LIMIT 1
            """,
            (username,)
        )


        existing_user = cursor.fetchone()


        if existing_user:

            print()

            print(
                f"Username '{username}' already exists."
            )

            return


        # =================================================
        # HASH PASSWORD
        # =================================================

        password_hash = generate_password_hash(
            password
        )


        # =================================================
        # INSERT USER
        # =================================================

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


        # =================================================
        # SUCCESS
        # =================================================

        print()

        print("=" * 50)

        print(
            "User created successfully!"
        )

        print("=" * 50)

        print(
            f"Username : {username}"
        )

        print(
            f"Role     : {role}"
        )

        print()

        print(
            "The user can now log in to Store Manager."
        )


    except Exception as error:

        # =================================================
        # ROLLBACK
        # =================================================

        if connection:

            connection.rollback()


        print()

        print(
            "Failed to create user."
        )

        print(
            f"Error: {error}"
        )


    finally:

        # =================================================
        # CLOSE DATABASE RESOURCES
        # =================================================

        if cursor:

            cursor.close()


        if connection:

            connection.close()


# =========================================================
# RUN SCRIPT
# =========================================================

if __name__ == "__main__":

    create_user()