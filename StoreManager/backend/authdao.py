from backend.db import get_connection


def get_user_by_username(username):
    """Return a user row by username, or None when no account exists."""
    connection = get_connection()
    cursor = connection.cursor(dictionary=True)

    try:
        cursor.execute(
            """
            SELECT user_id, username, password, role, employee_id
            FROM users
            WHERE username = %s
            LIMIT 1
            """,
            (username,),
        )
        return cursor.fetchone()
    finally:
        cursor.close()
        connection.close()
