from backend.db import get_connection


def get_suppliers():

    db = get_connection()
    cursor = db.cursor(dictionary=True)

    cursor.execute("""
        SELECT supplier_id, supplier_name
        FROM suppliers
        ORDER BY supplier_name
    """)

    suppliers = cursor.fetchall()

    cursor.close()
    db.close()

    return suppliers