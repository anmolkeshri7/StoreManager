from backend.db import get_connection


def get_categories():

    db = get_connection()
    cursor = db.cursor(dictionary=True)

    cursor.execute("""
        SELECT category_id, category_name
        FROM categories
        ORDER BY category_name
    """)

    categories = cursor.fetchall()

    cursor.close()
    db.close()

    return categories