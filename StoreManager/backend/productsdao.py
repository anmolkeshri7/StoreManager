from backend.db import get_connection


def add_product(product_name, category_id, supplier_id, barcode,
                purchase_price, selling_price, stock_quantity,
                reorder_level, unit):

    db = get_connection()
    cursor = db.cursor()

    query = """
    INSERT INTO products
    (product_name, category_id, supplier_id, barcode,
     purchase_price, selling_price, stock_quantity,
     reorder_level, unit)
    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
    """

    values = (
        product_name,
        category_id,
        supplier_id,
        barcode,
        purchase_price,
        selling_price,
        stock_quantity,
        reorder_level,
        unit
    )

    cursor.execute(query, values)
    db.commit()

    cursor.close()
    db.close()


def get_products():

    db = get_connection()
    cursor = db.cursor(dictionary=True)

    cursor.execute("SELECT * FROM products")

    products = cursor.fetchall()

    cursor.close()
    db.close()

    return products


def update_product(product_id, selling_price, stock_quantity):

    db = get_connection()
    cursor = db.cursor()

    query = """
    UPDATE products
    SET selling_price = %s,
        stock_quantity = %s
    WHERE product_id = %s
    """

    values = (
        selling_price,
        stock_quantity,
        product_id
    )

    cursor.execute(query, values)
    db.commit()

    cursor.close()
    db.close()


def delete_product(product_id):

    db = get_connection()
    cursor = db.cursor()

    query = """
    DELETE FROM products
    WHERE product_id = %s
    """

    cursor.execute(query, (product_id,))
    db.commit()

    cursor.close()
    db.close()
    
if __name__ == "__main__":

    # ADD
    add_product(
        "Test Product",
        1,
        1,
        "TEST001",
        100,
        150,
        20,
        5,
        "piece"
    )

    # VIEW
    products = get_products()

    for product in products:
        print(product)