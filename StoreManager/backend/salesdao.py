from backend.db import get_connection


# =========================================================
# GET ALL SALES
# =========================================================

def get_sales():

    db = get_connection()
    cursor = db.cursor(dictionary=True)

    try:

        query = """
            SELECT
                s.sale_id,
                s.sale_date,
                s.total_amount,
                s.discount,
                s.tax,
                s.final_amount,
                c.customer_name

            FROM sales s

            LEFT JOIN customers c
                ON s.customer_id = c.customer_id

            ORDER BY s.sale_id DESC
        """

        cursor.execute(query)

        return cursor.fetchall()

    finally:

        cursor.close()
        db.close()


# =========================================================
# GET SALE BY ID
# =========================================================

def get_sale_by_id(sale_id):

    db = get_connection()
    cursor = db.cursor(dictionary=True)

    try:

        query = """
            SELECT
                s.sale_id,
                s.customer_id,
                s.employee_id,
                s.sale_date,
                s.total_amount,
                s.discount,
                s.tax,
                s.final_amount,
                c.customer_name

            FROM sales s

            LEFT JOIN customers c
                ON s.customer_id = c.customer_id

            WHERE s.sale_id = %s
        """

        cursor.execute(
            query,
            (sale_id,)
        )

        return cursor.fetchone()

    finally:

        cursor.close()
        db.close()


# =========================================================
# GET SALE DETAILS
# =========================================================

def get_sale_details(sale_id):

    db = get_connection()
    cursor = db.cursor(dictionary=True)

    try:

        query = """
            SELECT
                sd.sale_detail_id,
                sd.sale_id,
                sd.product_id,
                sd.quantity,
                sd.selling_price,
                sd.purchase_price,
                sd.subtotal,
                p.product_name

            FROM sale_details sd

            LEFT JOIN products p
                ON sd.product_id = p.product_id

            WHERE sd.sale_id = %s

            ORDER BY sd.sale_detail_id
        """

        cursor.execute(
            query,
            (sale_id,)
        )

        return cursor.fetchall()

    finally:

        cursor.close()
        db.close()


# =========================================================
# GET SALE PAYMENTS
# =========================================================

def get_sale_payments(sale_id):

    db = get_connection()
    cursor = db.cursor(dictionary=True)

    try:

        query = """
            SELECT
                payment_id,
                sale_id,
                payment_date,
                amount,
                payment_method,
                payment_status

            FROM payments

            WHERE sale_id = %s

            ORDER BY payment_id DESC
        """

        cursor.execute(
            query,
            (sale_id,)
        )

        return cursor.fetchall()

    finally:

        cursor.close()
        db.close()


# =========================================================
# CREATE SALE
# =========================================================

def create_sale(
    customer_id,
    employee_id,
    items,
    discount,
    tax,
    payment_amount,
    payment_method
):

    db = get_connection()
    cursor = db.cursor(dictionary=True)

    try:

        # =================================================
        # START TRANSACTION
        # =================================================

        db.start_transaction()


        # =================================================
        # CALCULATE TOTAL
        # =================================================

        total_amount = 0


        validated_items = []


        for item in items:

            product_id = item["product_id"]

            quantity = item["quantity"]

            selling_price = item["selling_price"]


            # ---------------------------------------------
            # GET PRODUCT
            # ---------------------------------------------

            cursor.execute(
                """
                SELECT
                    product_id,
                    product_name,
                    stock_quantity,
                    purchase_price

                FROM products

                WHERE product_id = %s

                FOR UPDATE
                """,
                (product_id,)
            )


            product = cursor.fetchone()


            if product is None:

                raise ValueError(
                    f"Product ID {product_id} not found."
                )


            # ---------------------------------------------
            # STOCK VALIDATION
            # ---------------------------------------------

            if quantity > product["stock_quantity"]:

                raise ValueError(
                    f"Insufficient stock for "
                    f"{product['product_name']}. "
                    f"Available stock: "
                    f"{product['stock_quantity']}"
                )


            # ---------------------------------------------
            # PURCHASE PRICE
            # ---------------------------------------------

            purchase_price = float(
                product["purchase_price"]
            )


            # ---------------------------------------------
            # SUBTOTAL
            # ---------------------------------------------

            subtotal = (
                quantity *
                selling_price
            )


            total_amount += subtotal


            validated_items.append(
                {
                    "product_id":
                        product_id,

                    "quantity":
                        quantity,

                    "selling_price":
                        selling_price,

                    "purchase_price":
                        purchase_price,

                    "subtotal":
                        subtotal
                }
            )


        # =================================================
        # FINAL AMOUNT
        # =================================================

        final_amount = (
            total_amount
            - discount
            + tax
        )


        if final_amount < 0:

            raise ValueError(
                "Final amount cannot be negative."
            )


        # =================================================
        # PAYMENT STATUS
        # =================================================

        if payment_amount >= final_amount:

            payment_status = "Paid"

        elif payment_amount > 0:

            payment_status = "Partial"

        else:

            payment_status = "Pending"


        # =================================================
        # INSERT SALE
        # =================================================

        cursor.execute(
            """
            INSERT INTO sales
            (
                customer_id,
                employee_id,
                total_amount,
                discount,
                tax,
                final_amount
            )

            VALUES
            (
                %s,
                %s,
                %s,
                %s,
                %s,
                %s
            )
            """,
            (
                customer_id,
                employee_id,
                total_amount,
                discount,
                tax,
                final_amount
            )
        )


        sale_id = cursor.lastrowid


        # =================================================
        # INSERT SALE DETAILS + REDUCE STOCK
        # =================================================

        for item in validated_items:

            cursor.execute(
                """
                INSERT INTO sale_details
                (
                    sale_id,
                    product_id,
                    quantity,
                    selling_price,
                    purchase_price,
                    subtotal
                )

                VALUES
                (
                    %s,
                    %s,
                    %s,
                    %s,
                    %s,
                    %s
                )
                """,
                (
                    sale_id,
                    item["product_id"],
                    item["quantity"],
                    item["selling_price"],
                    item["purchase_price"],
                    item["subtotal"]
                )
            )


            # ---------------------------------------------
            # REDUCE STOCK
            # ---------------------------------------------

            cursor.execute(
                """
                UPDATE products

                SET stock_quantity =
                    stock_quantity - %s

                WHERE product_id = %s
                """,
                (
                    item["quantity"],
                    item["product_id"]
                )
            )


        # =================================================
        # INSERT PAYMENT
        # =================================================

        cursor.execute(
            """
            INSERT INTO payments
            (
                sale_id,
                amount,
                payment_method,
                payment_status
            )

            VALUES
            (
                %s,
                %s,
                %s,
                %s
            )
            """,
            (
                sale_id,
                payment_amount,
                payment_method,
                payment_status
            )
        )


        # =================================================
        # COMMIT
        # =================================================

        db.commit()


        return sale_id


    except Exception:

        db.rollback()

        raise


    finally:

        cursor.close()
        db.close()


# =========================================================
# DELETE SALE
# =========================================================

def delete_sale(sale_id):

    db = get_connection()
    cursor = db.cursor(dictionary=True)

    try:

        db.start_transaction()


        # =================================================
        # GET SALE ITEMS
        # =================================================

        cursor.execute(
            """
            SELECT
                product_id,
                quantity

            FROM sale_details

            WHERE sale_id = %s
            """,
            (sale_id,)
        )


        items = cursor.fetchall()


        # =================================================
        # RESTORE STOCK
        # =================================================

        for item in items:

            cursor.execute(
                """
                UPDATE products

                SET stock_quantity =
                    stock_quantity + %s

                WHERE product_id = %s
                """,
                (
                    item["quantity"],
                    item["product_id"]
                )
            )


        # =================================================
        # DELETE SALE
        # =================================================

        cursor.execute(
            """
            DELETE FROM sales

            WHERE sale_id = %s
            """,
            (sale_id,)
        )


        # payments and sale_details
        # are deleted automatically
        # through ON DELETE CASCADE


        db.commit()


    except Exception:

        db.rollback()

        raise


    finally:

        cursor.close()
        db.close()