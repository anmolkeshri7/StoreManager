from backend.db import get_connection


# =========================================================
# GET ALL PRODUCTS
# =========================================================

def get_products():

    db = get_connection()
    cursor = db.cursor(dictionary=True)

    query = """
        SELECT
            p.product_id,
            p.product_name,

            p.category_id,
            c.category_name,

            p.supplier_id,
            s.supplier_name,

            p.barcode,
            p.purchase_price,
            p.selling_price,
            p.stock_quantity,
            p.reorder_level,
            p.unit

        FROM products p

        LEFT JOIN categories c
            ON p.category_id = c.category_id

        LEFT JOIN suppliers s
            ON p.supplier_id = s.supplier_id

        ORDER BY p.product_id DESC
    """

    cursor.execute(query)

    products = cursor.fetchall()

    cursor.close()
    db.close()

    return products


# =========================================================
# GET PRODUCT BY ID
# =========================================================

def get_product_by_id(product_id):

    db = get_connection()
    cursor = db.cursor(dictionary=True)

    query = """
        SELECT
            p.product_id,
            p.product_name,

            p.category_id,
            c.category_name,

            p.supplier_id,
            s.supplier_name,

            p.barcode,
            p.purchase_price,
            p.selling_price,
            p.stock_quantity,
            p.reorder_level,
            p.unit

        FROM products p

        LEFT JOIN categories c
            ON p.category_id = c.category_id

        LEFT JOIN suppliers s
            ON p.supplier_id = s.supplier_id

        WHERE p.product_id = %s
    """

    cursor.execute(
        query,
        (product_id,)
    )

    product = cursor.fetchone()

    cursor.close()
    db.close()

    return product


# =========================================================
# ADD PRODUCT
# =========================================================

def add_product(
    product_name,
    category_id,
    supplier_id,
    barcode,
    purchase_price,
    selling_price,
    stock_quantity,
    reorder_level,
    unit
):

    db = get_connection()
    cursor = db.cursor()

    query = """
        INSERT INTO products
        (
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

        VALUES
        (
            %s,
            %s,
            %s,
            %s,
            %s,
            %s,
            %s,
            %s,
            %s
        )
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

    cursor.execute(
        query,
        values
    )

    db.commit()

    cursor.close()
    db.close()


# =========================================================
# UPDATE PRODUCT
# =========================================================

def update_product(
    product_id,
    product_name,
    category_id,
    supplier_id,
    barcode,
    purchase_price,
    selling_price,
    stock_quantity,
    reorder_level,
    unit
):

    db = get_connection()
    cursor = db.cursor()

    query = """
        UPDATE products

        SET
            product_name = %s,
            category_id = %s,
            supplier_id = %s,
            barcode = %s,
            purchase_price = %s,
            selling_price = %s,
            stock_quantity = %s,
            reorder_level = %s,
            unit = %s

        WHERE product_id = %s
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
        unit,
        product_id
    )

    cursor.execute(
        query,
        values
    )

    db.commit()

    cursor.close()
    db.close()


# =========================================================
# DELETE PRODUCT
# =========================================================

def delete_product(product_id):

    db = get_connection()
    cursor = db.cursor()

    query = """
        DELETE FROM products
        WHERE product_id = %s
    """

    cursor.execute(
        query,
        (product_id,)
    )

    db.commit()

    cursor.close()
    db.close()