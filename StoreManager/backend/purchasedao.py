from backend.db import get_connection


# =========================================================
# GET ALL PURCHASES
# =========================================================

def get_purchases():

    db = get_connection()
    cursor = db.cursor(dictionary=True)

    try:

        query = """
            SELECT
                p.purchase_id,
                p.supplier_id,
                p.employee_id,
                p.purchase_date,
                p.total_amount,

                s.supplier_name,

                e.employee_name

            FROM purchases p

            LEFT JOIN suppliers s
                ON p.supplier_id = s.supplier_id

            LEFT JOIN employees e
                ON p.employee_id = e.employee_id

            ORDER BY p.purchase_id DESC
        """

        cursor.execute(query)

        return cursor.fetchall()

    finally:

        cursor.close()
        db.close()


# =========================================================
# GET PURCHASE BY ID
# =========================================================

def get_purchase_by_id(purchase_id):

    db = get_connection()
    cursor = db.cursor(dictionary=True)

    try:

        query = """
            SELECT
                p.purchase_id,
                p.supplier_id,
                p.employee_id,
                p.purchase_date,
                p.total_amount,

                s.supplier_name,

                e.employee_name

            FROM purchases p

            LEFT JOIN suppliers s
                ON p.supplier_id = s.supplier_id

            LEFT JOIN employees e
                ON p.employee_id = e.employee_id

            WHERE p.purchase_id = %s
        """

        cursor.execute(
            query,
            (purchase_id,)
        )

        return cursor.fetchone()

    finally:

        cursor.close()
        db.close()


# =========================================================
# GET PURCHASE DETAILS
# =========================================================

def get_purchase_details(purchase_id):

    db = get_connection()
    cursor = db.cursor(dictionary=True)

    try:

        query = """
            SELECT
                pi.purchase_item_id,
                pi.purchase_id,
                pi.product_id,
                pi.quantity,
                pi.purchase_price,
                pi.subtotal,

                p.product_name

            FROM purchase_items pi

            INNER JOIN products p
                ON pi.product_id = p.product_id

            WHERE pi.purchase_id = %s

            ORDER BY pi.purchase_item_id
        """

        cursor.execute(
            query,
            (purchase_id,)
        )

        return cursor.fetchall()

    finally:

        cursor.close()
        db.close()


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

        # =================================================
        # BASIC VALIDATION
        # =================================================

        if not supplier_id:

            raise ValueError(
                "Please select a supplier."
            )


        if not items:

            raise ValueError(
                "A purchase must contain at least one item."
            )


        # =================================================
        # VERIFY SUPPLIER
        # =================================================

        cursor.execute(
            """
            SELECT supplier_id

            FROM suppliers

            WHERE supplier_id = %s
            """,
            (
                supplier_id,
            )
        )

        supplier = cursor.fetchone()


        if supplier is None:

            raise ValueError(
                "Selected supplier does not exist."
            )


        # =================================================
        # VERIFY EMPLOYEE
        # =================================================

        if employee_id is not None:

            cursor.execute(
                """
                SELECT employee_id

                FROM employees

                WHERE employee_id = %s
                """,
                (
                    employee_id,
                )
            )

            employee = cursor.fetchone()


            if employee is None:

                raise ValueError(
                    "Selected employee does not exist."
                )


        # =================================================
        # VALIDATE AND NORMALIZE ITEMS
        # =================================================

        normalized_items = []

        total_amount = 0


        for item in items:

            product_id = item.get(
                "product_id"
            )

            quantity = item.get(
                "quantity"
            )

            purchase_price = item.get(
                "purchase_price"
            )


            # ---------------------------------------------
            # PRODUCT ID
            # ---------------------------------------------

            if product_id is None:

                raise ValueError(
                    "Every purchase item must have a product."
                )


            try:

                product_id = int(
                    product_id
                )

            except (TypeError, ValueError):

                raise ValueError(
                    "Invalid product ID."
                )


            if product_id <= 0:

                raise ValueError(
                    "Invalid product ID."
                )


            # ---------------------------------------------
            # QUANTITY
            # ---------------------------------------------

            try:

                quantity = int(
                    quantity
                )

            except (TypeError, ValueError):

                raise ValueError(
                    "Purchase quantity must be a valid number."
                )


            if quantity <= 0:

                raise ValueError(
                    "Purchase quantity must be greater than zero."
                )


            # ---------------------------------------------
            # PURCHASE PRICE
            # ---------------------------------------------

            try:

                purchase_price = float(
                    purchase_price
                )

            except (TypeError, ValueError):

                raise ValueError(
                    "Purchase price must be a valid number."
                )


            if purchase_price < 0:

                raise ValueError(
                    "Purchase price cannot be negative."
                )


            # ---------------------------------------------
            # CHECK PRODUCT
            # ---------------------------------------------

            cursor.execute(
                """
                SELECT
                    product_id,
                    product_name,
                    COALESCE(stock_quantity, 0)
                        AS stock_quantity

                FROM products

                WHERE product_id = %s

                FOR UPDATE
                """,
                (
                    product_id,
                )
            )

            product = cursor.fetchone()


            if product is None:

                raise ValueError(
                    f"Product ID {product_id} does not exist."
                )


            # ---------------------------------------------
            # CALCULATE SUBTOTAL
            # ---------------------------------------------

            subtotal = (
                quantity
                * purchase_price
            )


            # ---------------------------------------------
            # STORE NORMALIZED ITEM
            # ---------------------------------------------

            normalized_items.append(
                {
                    "product_id":
                        product_id,

                    "quantity":
                        quantity,

                    "purchase_price":
                        purchase_price,

                    "subtotal":
                        subtotal
                }
            )


            total_amount += subtotal


        # =================================================
        # COMBINE DUPLICATE PRODUCTS
        # =================================================

        combined_items = {}


        for item in normalized_items:

            product_id = item[
                "product_id"
            ]


            if product_id not in combined_items:

                combined_items[
                    product_id
                ] = {

                    "product_id":
                        product_id,

                    "quantity":
                        item["quantity"],

                    "purchase_price":
                        item["purchase_price"],

                    "subtotal":
                        item["subtotal"]

                }

            else:

                combined_items[
                    product_id
                ]["quantity"] += item[
                    "quantity"
                ]

                combined_items[
                    product_id
                ]["subtotal"] += item[
                    "subtotal"
                ]


        normalized_items = list(
            combined_items.values()
        )


        # =================================================
        # RECALCULATE TOTAL
        # =================================================

        total_amount = sum(
            item["subtotal"]
            for item in normalized_items
        )


        # =================================================
        # INSERT PURCHASE
        # =================================================

        cursor.execute(
            """
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
            """,
            (
                supplier_id,
                employee_id,
                total_amount
            )
        )


        purchase_id = cursor.lastrowid


        # =================================================
        # INSERT PURCHASE ITEMS
        # =================================================

        for item in normalized_items:

            cursor.execute(
                """
                INSERT INTO purchase_items
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
                """,
                (
                    purchase_id,
                    item["product_id"],
                    item["quantity"],
                    item["purchase_price"],
                    item["subtotal"]
                )
            )


        # =================================================
        # UPDATE PRODUCT STOCK
        # =================================================

        for item in normalized_items:

            cursor.execute(
                """
                UPDATE products

                SET stock_quantity =
                    COALESCE(stock_quantity, 0)
                    + %s

                WHERE product_id = %s
                """,
                (
                    item["quantity"],
                    item["product_id"]
                )
            )


            if cursor.rowcount == 0:

                raise ValueError(
                    f"Unable to update stock for "
                    f"product ID {item['product_id']}."
                )


        # =================================================
        # COMMIT TRANSACTION
        # =================================================

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

        # =================================================
        # GET PURCHASE ITEMS
        # =================================================

        cursor.execute(
            """
            SELECT
                pi.product_id,
                pi.quantity,

                p.product_name,

                COALESCE(
                    p.stock_quantity,
                    0
                ) AS stock_quantity

            FROM purchase_items pi

            INNER JOIN products p
                ON pi.product_id = p.product_id

            WHERE pi.purchase_id = %s

            FOR UPDATE
            """,
            (
                purchase_id,
            )
        )

        items = cursor.fetchall()


        # =================================================
        # CHECK PURCHASE EXISTS
        # =================================================

        if not items:

            cursor.execute(
                """
                SELECT purchase_id

                FROM purchases

                WHERE purchase_id = %s
                """,
                (
                    purchase_id,
                )
            )

            purchase = cursor.fetchone()


            if purchase is None:

                raise ValueError(
                    "Purchase not found."
                )


        # =================================================
        # CHECK STOCK BEFORE REVERSING
        # =================================================

        for item in items:

            current_stock = int(
                item["stock_quantity"] or 0
            )

            purchase_quantity = int(
                item["quantity"]
            )


            if current_stock < purchase_quantity:

                raise ValueError(
                    f"Cannot delete this purchase "
                    f"because stock for "
                    f"'{item['product_name']}' "
                    f"would become negative."
                )


        # =================================================
        # RESTORE / REDUCE STOCK
        # =================================================

        for item in items:

            cursor.execute(
                """
                UPDATE products

                SET stock_quantity =
                    COALESCE(stock_quantity, 0)
                    - %s

                WHERE product_id = %s
                """,
                (
                    item["quantity"],
                    item["product_id"]
                )
            )


        # =================================================
        # DELETE PURCHASE
        # =================================================

        cursor.execute(
            """
            DELETE FROM purchases

            WHERE purchase_id = %s
            """,
            (
                purchase_id,
            )
        )


        if cursor.rowcount == 0:

            raise ValueError(
                "Purchase not found."
            )


        # =================================================
        # COMMIT
        # =================================================

        db.commit()


    except Exception:

        db.rollback()

        raise


    finally:

        cursor.close()
        db.close()