from backend.db import get_connection


# =========================================================
# GET DASHBOARD STATISTICS
# =========================================================

def get_dashboard_stats():

    db = get_connection()
    cursor = db.cursor(dictionary=True)

    stats = {}

    try:

        # =================================================
        # TOTAL PRODUCTS
        # =================================================

        cursor.execute("""
            SELECT COUNT(*) AS total_products
            FROM products
        """)

        result = cursor.fetchone()

        stats["total_products"] = (
            result["total_products"] or 0
        )


        # =================================================
        # TOTAL CUSTOMERS
        # =================================================

        cursor.execute("""
            SELECT COUNT(*) AS total_customers
            FROM customers
        """)

        result = cursor.fetchone()

        stats["total_customers"] = (
            result["total_customers"] or 0
        )


        # =================================================
        # TOTAL SUPPLIERS
        # =================================================

        cursor.execute("""
            SELECT COUNT(*) AS total_suppliers
            FROM suppliers
        """)

        result = cursor.fetchone()

        stats["total_suppliers"] = (
            result["total_suppliers"] or 0
        )


        # =================================================
        # TOTAL CATEGORIES
        # =================================================

        cursor.execute("""
            SELECT COUNT(*) AS total_categories
            FROM categories
        """)

        result = cursor.fetchone()

        stats["total_categories"] = (
            result["total_categories"] or 0
        )


        # =================================================
        # TOTAL SALES
        # =================================================

        cursor.execute("""
            SELECT COUNT(*) AS total_sales
            FROM sales
        """)

        result = cursor.fetchone()

        stats["total_sales"] = (
            result["total_sales"] or 0
        )


        # =================================================
        # TOTAL SALES VALUE
        # =================================================

        cursor.execute("""
            SELECT
                COALESCE(
                    SUM(final_amount),
                    0
                ) AS total_sales_value

            FROM sales
        """)

        result = cursor.fetchone()

        stats["total_sales_value"] = (
            result["total_sales_value"] or 0
        )


        # =================================================
        # TODAY'S SALES
        # =================================================

        cursor.execute("""
            SELECT
                COALESCE(
                    SUM(final_amount),
                    0
                ) AS today_sales

            FROM sales

            WHERE DATE(sale_date) = CURDATE()
        """)

        result = cursor.fetchone()

        stats["today_sales"] = (
            result["today_sales"] or 0
        )


        # =================================================
        # TODAY'S SALE COUNT
        # =================================================

        cursor.execute("""
            SELECT COUNT(*) AS today_sale_count

            FROM sales

            WHERE DATE(sale_date) = CURDATE()
        """)

        result = cursor.fetchone()

        stats["today_sale_count"] = (
            result["today_sale_count"] or 0
        )


        # =================================================
        # TOTAL PURCHASE VALUE
        # =================================================

        cursor.execute("""
            SELECT
                COALESCE(
                    SUM(total_amount),
                    0
                ) AS total_purchase_value

            FROM purchases
        """)

        result = cursor.fetchone()

        stats["total_purchase_value"] = (
            result["total_purchase_value"] or 0
        )


        # =================================================
        # TOTAL STOCK
        # =================================================

        cursor.execute("""
            SELECT
                COALESCE(
                    SUM(stock_quantity),
                    0
                ) AS total_stock

            FROM products
        """)

        result = cursor.fetchone()

        stats["total_stock"] = (
            result["total_stock"] or 0
        )


        # =================================================
        # INVENTORY VALUE
        # =================================================

        cursor.execute("""
            SELECT
                COALESCE(
                    SUM(
                        stock_quantity
                        * purchase_price
                    ),
                    0
                ) AS inventory_value

            FROM products
        """)

        result = cursor.fetchone()

        stats["inventory_value"] = (
            result["inventory_value"] or 0
        )


        # =================================================
        # LOW STOCK
        # =================================================

        cursor.execute("""
            SELECT COUNT(*) AS low_stock_count

            FROM products

            WHERE stock_quantity <= reorder_level
        """)

        result = cursor.fetchone()

        stats["low_stock_count"] = (
            result["low_stock_count"] or 0
        )


        # =================================================
        # OUT OF STOCK
        # =================================================

        cursor.execute("""
            SELECT COUNT(*) AS out_of_stock_count

            FROM products

            WHERE stock_quantity = 0
        """)

        result = cursor.fetchone()

        stats["out_of_stock_count"] = (
            result["out_of_stock_count"] or 0
        )


        # =================================================
        # COST OF GOODS SOLD
        #
        # COGS =
        # quantity sold × historical purchase price
        # =================================================

        cursor.execute("""
            SELECT
                COALESCE(
                    SUM(
                        quantity
                        * purchase_price
                    ),
                    0
                ) AS cost_of_goods_sold

            FROM sale_details
        """)

        result = cursor.fetchone()

        stats["cost_of_goods_sold"] = (
            result["cost_of_goods_sold"] or 0
        )


        # =================================================
        # GROSS PROFIT
        #
        # Gross Profit =
        # Selling Revenue - Product Cost
        # =================================================

        cursor.execute("""
            SELECT
                COALESCE(
                    SUM(
                        quantity
                        * (
                            selling_price
                            - purchase_price
                        )
                    ),
                    0
                ) AS gross_profit

            FROM sale_details
        """)

        result = cursor.fetchone()

        stats["gross_profit"] = (
            result["gross_profit"] or 0
        )


        # =================================================
        # PROFIT MARGIN
        #
        # Profit Margin =
        # Gross Profit / Sales Revenue × 100
        # =================================================

        if float(stats["total_sales_value"]) > 0:

            stats["profit_margin"] = (

                float(stats["gross_profit"])
                /
                float(stats["total_sales_value"])

            ) * 100

        else:

            stats["profit_margin"] = 0


        # =================================================
        # RETURN ALL STATISTICS
        # =================================================

        return stats


    finally:

        cursor.close()
        db.close()


# =========================================================
# GET RECENT SALES
# =========================================================

def get_recent_sales(limit=5):

    db = get_connection()
    cursor = db.cursor(dictionary=True)

    try:

        query = """
            SELECT
                s.sale_id,
                s.sale_date,
                s.final_amount,
                c.customer_name

            FROM sales s

            LEFT JOIN customers c
                ON s.customer_id = c.customer_id

            ORDER BY s.sale_id DESC

            LIMIT %s
        """

        cursor.execute(
            query,
            (limit,)
        )

        return cursor.fetchall()

    finally:

        cursor.close()
        db.close()


# =========================================================
# GET LOW STOCK PRODUCTS
# =========================================================

def get_low_stock_products(limit=5):

    db = get_connection()
    cursor = db.cursor(dictionary=True)

    try:

        query = """
            SELECT
                product_id,
                product_name,
                stock_quantity,
                reorder_level,
                unit

            FROM products

            WHERE stock_quantity <= reorder_level

            ORDER BY stock_quantity ASC

            LIMIT %s
        """

        cursor.execute(
            query,
            (limit,)
        )

        return cursor.fetchall()

    finally:

        cursor.close()
        db.close()


# =========================================================
# GET TOP SELLING PRODUCTS
# =========================================================

def get_top_selling_products(limit=5):

    db = get_connection()
    cursor = db.cursor(dictionary=True)

    try:

        query = """
            SELECT
                p.product_id,
                p.product_name,
                SUM(sd.quantity)
                AS total_quantity_sold

            FROM sale_details sd

            INNER JOIN products p
                ON sd.product_id = p.product_id

            GROUP BY
                p.product_id,
                p.product_name

            ORDER BY
                total_quantity_sold DESC

            LIMIT %s
        """

        cursor.execute(
            query,
            (limit,)
        )

        return cursor.fetchall()

    finally:

        cursor.close()
        db.close()


# =========================================================
# GET MONTHLY SALES
# =========================================================

def get_monthly_sales():

    db = get_connection()
    cursor = db.cursor(dictionary=True)

    try:

        query = """
            SELECT
                DATE_FORMAT(
                    sale_date,
                    '%Y-%m'
                ) AS month,

                COALESCE(
                    SUM(final_amount),
                    0
                ) AS total_sales

            FROM sales

            WHERE sale_date >= DATE_SUB(
                CURDATE(),
                INTERVAL 5 MONTH
            )

            GROUP BY
                DATE_FORMAT(
                    sale_date,
                    '%Y-%m'
                )

            ORDER BY month
        """

        cursor.execute(query)

        return cursor.fetchall()

    finally:

        cursor.close()
        db.close()


# =========================================================
# GET SALES BY CATEGORY
# =========================================================

def get_sales_by_category():

    db = get_connection()
    cursor = db.cursor(dictionary=True)

    try:

        query = """
            SELECT
                c.category_name,

                COALESCE(
                    SUM(sd.subtotal),
                    0
                ) AS total_sales

            FROM sale_details sd

            INNER JOIN products p
                ON sd.product_id = p.product_id

            INNER JOIN categories c
                ON p.category_id = c.category_id

            GROUP BY
                c.category_id,
                c.category_name

            ORDER BY
                total_sales DESC
        """

        cursor.execute(query)

        return cursor.fetchall()

    finally:

        cursor.close()
        db.close()