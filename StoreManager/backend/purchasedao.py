from backend.db import get_connection


# =========================================================
# GET ALL PURCHASES
# =========================================================

def get_purchases():

    db = get_connection()

    cursor = db.cursor(dictionary=True)

    query = """
        SELECT
            p.purchase_id,
            p.supplier_id,
            s.supplier_name,
            p.employee_id,
            p.purchase_date,
            p.total_amount

        FROM purchases p

        LEFT JOIN suppliers s
            ON p.supplier_id = s.supplier_id

        ORDER BY p.purchase_id DESC
    """

    cursor.execute(query)

    purchases = cursor.fetchall()

    cursor.close()

    db.close()

    return purchases


# =========================================================
# GET PURCHASE BY ID
# =========================================================

def get_purchase_by_id(purchase_id):

    db = get_connection()

    cursor = db.cursor(dictionary=True)

    query = """
        SELECT
            p.purchase_id,
            p.supplier_id,
            s.supplier_name,
            p.employee_id,
            p.purchase_date,
            p.total_amount

        FROM purchases p

        LEFT JOIN suppliers s
            ON p.supplier_id = s.supplier_id

        WHERE p.purchase_id = %s
    """

    cursor.execute(
        query,
        (purchase_id,)
    )

    purchase = cursor.fetchone()

    cursor.close()

    db.close()

    return purchase


# =========================================================
# GET PURCHASE DETAILS
# =========================================================

def get_purchase_details(purchase_id):

    db = get_connection()

    cursor = db.cursor(dictionary=True)

    query = """
        SELECT
            pd.purchase_detail_id,
            pd.purchase_id,
            pd.product_id,
            p.product_name,
            pd.quantity,
            pd.purchase_price,
            pd.subtotal

        FROM purchase_details pd

        LEFT JOIN products p
            ON pd.product_id = p.product_id

        WHERE pd.purchase_id = %s

        ORDER BY pd.purchase_detail_id
    """

    cursor.execute(
        query,
        (purchase_id,)
    )

    details = cursor.fetchall()

    cursor.close()

    db.close()

    return details


# =========================================================
# CREATE PURCHASE
# =========================================================

def create_purchase(
    supplier_id,
    employee_id,
    items
):

    db = get_connection()

    cursor = db.cursor(dictionary=True)

    try:

        # -------------------------------------------------
        # Calculate total
        # -------------------------------------------------

        total_amount = 0

        for item in items:

            subtotal = (
                item["quantity"]
                * item["purchase_price"]
            )

            total_amount += subtotal


        # -------------------------------------------------
        # Insert purchase
        # -------------------------------------------------

        purchase_query = """
            INSERT INTO purchases
            (
                supplier_id,
                employee_id,
                total_amount
            )

            VALUES
            (
                %s,
                %s,
                %s
            )
        """

        cursor.execute(
            purchase_query,
            (
                supplier_id,
                employee_id,
                total_amount
            )
        )


        purchase_id = cursor.lastrowid


        # -------------------------------------------------
        # Insert purchase details
        # -------------------------------------------------

        detail_query = """
            INSERT INTO purchase_details
            (
                purchase_id,
                product_id,
                quantity,
                purchase_price,
                subtotal
            )

            VALUES
            (
                %s,
                %s,
                %s,
                %s,
                %s
            )
        """


        # -------------------------------------------------
        # Update product stock
        # -------------------------------------------------

        stock_query = """
            UPDATE products

            SET
                stock_quantity =
                    stock_quantity + %s,

                purchase_price = %s

            WHERE product_id = %s
        """


        for item in items:

            quantity = item["quantity"]

            purchase_price = item[
                "purchase_price"
            ]

            subtotal = (
                quantity
                * purchase_price
            )


            # Insert detail

            cursor.execute(
                detail_query,
                (
                    purchase_id,
                    item["product_id"],
                    quantity,
                    purchase_price,
                    subtotal
                )
            )


            # Increase stock

            cursor.execute(
                stock_query,
                (
                    quantity,
                    purchase_price,
                    item["product_id"]
                )
            )


        # -------------------------------------------------
        # Commit transaction
        # -------------------------------------------------

        db.commit()

        return purchase_id


    except Exception:

        db.rollback()

        raise


    finally:

        cursor.close()

        db.close()


# =========================================================
# DELETE PURCHASE
# =========================================================

def delete_purchase(purchase_id):

    db = get_connection()

    cursor = db.cursor(dictionary=True)

    try:

        # -------------------------------------------------
        # Get purchase details first
        # -------------------------------------------------

        detail_query = """
            SELECT
                product_id,
                quantity

            FROM purchase_details

            WHERE purchase_id = %s
        """

        cursor.execute(
            detail_query,
            (purchase_id,)
        )

        details = cursor.fetchall()


        # -------------------------------------------------
        # Reduce stock
        # -------------------------------------------------

        stock_query = """
            UPDATE products

            SET
                stock_quantity =
                    stock_quantity - %s

            WHERE product_id = %s
        """


        for detail in details:

            cursor.execute(
                stock_query,
                (
                    detail["quantity"],
                    detail["product_id"]
                )
            )


        # -------------------------------------------------
        # Delete purchase
        # -------------------------------------------------

        delete_query = """
            DELETE FROM purchases

            WHERE purchase_id = %s
        """

        cursor.execute(
            delete_query,
            (purchase_id,)
        )


        db.commit()


    except Exception:

        db.rollback()

        raise


    finally:

        cursor.close()

        db.close()