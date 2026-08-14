from backend.db import get_connection


# =========================================================
# GET ALL SUPPLIERS
# =========================================================

def get_suppliers():

    db = get_connection()

    cursor = db.cursor(dictionary=True)

    query = """
        SELECT
            supplier_id,
            supplier_name,
            phone,
            email,
            address
        FROM suppliers
        ORDER BY supplier_id DESC
    """

    cursor.execute(query)

    suppliers = cursor.fetchall()

    cursor.close()

    db.close()

    return suppliers


# =========================================================
# GET SUPPLIER BY ID
# =========================================================

def get_supplier_by_id(supplier_id):

    db = get_connection()

    cursor = db.cursor(dictionary=True)

    query = """
        SELECT
            supplier_id,
            supplier_name,
            phone,
            email,
            address
        FROM suppliers
        WHERE supplier_id = %s
    """

    cursor.execute(
        query,
        (supplier_id,)
    )

    supplier = cursor.fetchone()

    cursor.close()

    db.close()

    return supplier


# =========================================================
# ADD SUPPLIER
# =========================================================

def add_supplier(
    supplier_name,
    phone,
    email,
    address
):

    db = get_connection()

    cursor = db.cursor()

    query = """
        INSERT INTO suppliers
        (
            supplier_name,
            phone,
            email,
            address
        )
        VALUES
        (
            %s,
            %s,
            %s,
            %s
        )
    """

    values = (
        supplier_name,
        phone,
        email,
        address
    )

    cursor.execute(
        query,
        values
    )

    db.commit()

    cursor.close()

    db.close()


# =========================================================
# UPDATE SUPPLIER
# =========================================================

def update_supplier(
    supplier_id,
    supplier_name,
    phone,
    email,
    address
):

    db = get_connection()

    cursor = db.cursor()

    query = """
        UPDATE suppliers

        SET
            supplier_name = %s,
            phone = %s,
            email = %s,
            address = %s

        WHERE supplier_id = %s
    """

    values = (
        supplier_name,
        phone,
        email,
        address,
        supplier_id
    )

    cursor.execute(
        query,
        values
    )

    db.commit()

    cursor.close()

    db.close()


# =========================================================
# DELETE SUPPLIER
# =========================================================

def delete_supplier(supplier_id):

    db = get_connection()

    cursor = db.cursor()

    query = """
        DELETE FROM suppliers
        WHERE supplier_id = %s
    """

    cursor.execute(
        query,
        (supplier_id,)
    )

    db.commit()

    cursor.close()

    db.close()