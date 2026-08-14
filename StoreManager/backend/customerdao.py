from backend.db import get_connection


# =========================================================
# GET ALL CUSTOMERS
# =========================================================

def get_customers():

    db = get_connection()

    cursor = db.cursor(dictionary=True)

    query = """
        SELECT
            customer_id,
            customer_name,
            phone,
            email,
            address
        FROM customers
        ORDER BY customer_id DESC
    """

    cursor.execute(query)

    customers = cursor.fetchall()

    cursor.close()
    db.close()

    return customers


# =========================================================
# GET CUSTOMER BY ID
# =========================================================

def get_customer_by_id(customer_id):

    db = get_connection()

    cursor = db.cursor(dictionary=True)

    query = """
        SELECT
            customer_id,
            customer_name,
            phone,
            email,
            address
        FROM customers
        WHERE customer_id = %s
    """

    cursor.execute(
        query,
        (customer_id,)
    )

    customer = cursor.fetchone()

    cursor.close()
    db.close()

    return customer


# =========================================================
# ADD CUSTOMER
# =========================================================

def add_customer(
    customer_name,
    phone,
    email,
    address
):

    db = get_connection()

    cursor = db.cursor()

    query = """
        INSERT INTO customers
        (
            customer_name,
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
        customer_name,
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
# UPDATE CUSTOMER
# =========================================================

def update_customer(
    customer_id,
    customer_name,
    phone,
    email,
    address
):

    db = get_connection()

    cursor = db.cursor()

    query = """
        UPDATE customers

        SET
            customer_name = %s,
            phone = %s,
            email = %s,
            address = %s

        WHERE customer_id = %s
    """

    values = (
        customer_name,
        phone,
        email,
        address,
        customer_id
    )

    cursor.execute(
        query,
        values
    )

    db.commit()

    cursor.close()
    db.close()


# =========================================================
# DELETE CUSTOMER
# =========================================================

def delete_customer(customer_id):

    db = get_connection()

    cursor = db.cursor()

    query = """
        DELETE FROM customers
        WHERE customer_id = %s
    """

    cursor.execute(
        query,
        (customer_id,)
    )

    db.commit()

    cursor.close()
    db.close()