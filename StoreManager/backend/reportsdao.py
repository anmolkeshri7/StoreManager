from backend.db import get_connection


# =========================================================
# SALES SUMMARY
# =========================================================

def get_sales_summary(
    start_date=None,
    end_date=None
):

    db = get_connection()
    cursor = db.cursor(dictionary=True)

    try:

        query = """
            SELECT

                COUNT(DISTINCT s.sale_id)
                    AS total_sales,

                COALESCE(
                    SUM(sd.quantity),
                    0
                )
                    AS total_items_sold,

                COALESCE(
                    SUM(sd.subtotal),
                    0
                )
                    AS gross_sales,

                COALESCE(
                    SUM(s.discount),
                    0
                )
                    AS total_discount,

                COALESCE(
                    SUM(s.tax),
                    0
                )
                    AS total_tax,

                COALESCE(
                    SUM(s.final_amount),
                    0
                )
                    AS net_sales

            FROM sales s

            LEFT JOIN sale_details sd
                ON s.sale_id = sd.sale_id

            WHERE 1 = 1
        """

        params = []


        if start_date:

            query += """
                AND DATE(s.sale_date) >= %s
            """

            params.append(start_date)


        if end_date:

            query += """
                AND DATE(s.sale_date) <= %s
            """

            params.append(end_date)


        cursor.execute(
            query,
            tuple(params)
        )

        result = cursor.fetchone()


        if result is None:

            return {
                "total_sales": 0,
                "total_items_sold": 0,
                "gross_sales": 0,
                "total_discount": 0,
                "total_tax": 0,
                "net_sales": 0
            }


        return result

    finally:

        cursor.close()
        db.close()


# =========================================================
# PROFIT SUMMARY
# =========================================================

def get_profit_summary(
    start_date=None,
    end_date=None
):

    db = get_connection()
    cursor = db.cursor(dictionary=True)

    try:

        query = """
            SELECT

                COALESCE(
                    SUM(sd.subtotal),
                    0
                )
                    AS revenue,

                COALESCE(
                    SUM(
                        sd.quantity
                        * sd.purchase_price
                    ),
                    0
                )
                    AS cogs,

                COALESCE(
                    SUM(
                        sd.subtotal
                        -
                        (
                            sd.quantity
                            * sd.purchase_price
                        )
                    ),
                    0
                )
                    AS gross_profit

            FROM sales s

            INNER JOIN sale_details sd
                ON s.sale_id = sd.sale_id

            WHERE 1 = 1
        """

        params = []


        if start_date:

            query += """
                AND DATE(s.sale_date) >= %s
            """

            params.append(start_date)


        if end_date:

            query += """
                AND DATE(s.sale_date) <= %s
            """

            params.append(end_date)


        cursor.execute(
            query,
            tuple(params)
        )

        result = cursor.fetchone()


        if result is None:

            return {
                "revenue": 0,
                "cogs": 0,
                "gross_profit": 0,
                "profit_margin": 0
            }


        revenue = float(
            result["revenue"] or 0
        )

        cogs = float(
            result["cogs"] or 0
        )

        gross_profit = float(
            result["gross_profit"] or 0
        )


        if revenue > 0:

            profit_margin = (
                gross_profit
                / revenue
            ) * 100

        else:

            profit_margin = 0


        return {

            "revenue":
                revenue,

            "cogs":
                cogs,

            "gross_profit":
                gross_profit,

            "profit_margin":
                profit_margin

        }

    finally:

        cursor.close()
        db.close()


# =========================================================
# DAILY SALES
# =========================================================

def get_daily_sales(
    start_date=None,
    end_date=None
):

    db = get_connection()
    cursor = db.cursor(dictionary=True)

    try:

        query = """
            SELECT

                DATE(s.sale_date)
                    AS sale_date,

                COUNT(
                    DISTINCT s.sale_id
                )
                    AS number_of_sales,

                COALESCE(
                    SUM(s.final_amount),
                    0
                )
                    AS total_sales

            FROM sales s

            WHERE 1 = 1
        """

        params = []


        if start_date:

            query += """
                AND DATE(s.sale_date) >= %s
            """

            params.append(start_date)


        if end_date:

            query += """
                AND DATE(s.sale_date) <= %s
            """

            params.append(end_date)


        query += """

            GROUP BY DATE(s.sale_date)

            ORDER BY DATE(s.sale_date)
        """


        cursor.execute(
            query,
            tuple(params)
        )

        return cursor.fetchall()

    finally:

        cursor.close()
        db.close()


# =========================================================
# TOP SELLING PRODUCTS
# =========================================================

def get_top_selling_products(
    start_date=None,
    end_date=None,
    limit=10
):

    db = get_connection()
    cursor = db.cursor(dictionary=True)

    try:

        query = """
            SELECT

                p.product_id,

                p.product_name,

                COALESCE(
                    SUM(sd.quantity),
                    0
                )
                    AS quantity_sold,

                COALESCE(
                    SUM(sd.subtotal),
                    0
                )
                    AS revenue,

                COALESCE(
                    SUM(
                        sd.quantity
                        * sd.purchase_price
                    ),
                    0
                )
                    AS cogs,

                COALESCE(
                    SUM(
                        sd.subtotal
                        -
                        (
                            sd.quantity
                            * sd.purchase_price
                        )
                    ),
                    0
                )
                    AS profit

            FROM sale_details sd

            INNER JOIN sales s
                ON sd.sale_id = s.sale_id

            INNER JOIN products p
                ON sd.product_id = p.product_id

            WHERE 1 = 1
        """

        params = []


        if start_date:

            query += """
                AND DATE(s.sale_date) >= %s
            """

            params.append(start_date)


        if end_date:

            query += """
                AND DATE(s.sale_date) <= %s
            """

            params.append(end_date)


        query += """

            GROUP BY
                p.product_id,
                p.product_name

            ORDER BY
                quantity_sold DESC

            LIMIT %s
        """

        params.append(int(limit))


        cursor.execute(
            query,
            tuple(params)
        )

        return cursor.fetchall()

    finally:

        cursor.close()
        db.close()


# =========================================================
# SALES BY CATEGORY
# =========================================================

def get_sales_by_category(
    start_date=None,
    end_date=None
):

    db = get_connection()
    cursor = db.cursor(dictionary=True)

    try:

        query = """
            SELECT

                c.category_id,

                c.category_name,

                COALESCE(
                    SUM(sd.quantity),
                    0
                )
                    AS quantity_sold,

                COALESCE(
                    SUM(sd.subtotal),
                    0
                )
                    AS revenue,

                COALESCE(
                    SUM(
                        sd.subtotal
                        -
                        (
                            sd.quantity
                            * sd.purchase_price
                        )
                    ),
                    0
                )
                    AS profit

            FROM sale_details sd

            INNER JOIN sales s
                ON sd.sale_id = s.sale_id

            INNER JOIN products p
                ON sd.product_id = p.product_id

            INNER JOIN categories c
                ON p.category_id = c.category_id

            WHERE 1 = 1
        """

        params = []


        if start_date:

            query += """
                AND DATE(s.sale_date) >= %s
            """

            params.append(start_date)


        if end_date:

            query += """
                AND DATE(s.sale_date) <= %s
            """

            params.append(end_date)


        query += """

            GROUP BY
                c.category_id,
                c.category_name

            ORDER BY
                revenue DESC
        """


        cursor.execute(
            query,
            tuple(params)
        )

        return cursor.fetchall()

    finally:

        cursor.close()
        db.close()


# =========================================================
# CUSTOMER SALES
# =========================================================

def get_customer_sales(
    start_date=None,
    end_date=None,
    limit=10
):

    db = get_connection()
    cursor = db.cursor(dictionary=True)

    try:

        query = """
            SELECT

                c.customer_id,

                c.customer_name,

                COUNT(
                    DISTINCT s.sale_id
                )
                    AS number_of_sales,

                COALESCE(
                    SUM(s.final_amount),
                    0
                )
                    AS total_spent

            FROM sales s

            INNER JOIN customers c
                ON s.customer_id = c.customer_id

            WHERE 1 = 1
        """

        params = []


        if start_date:

            query += """
                AND DATE(s.sale_date) >= %s
            """

            params.append(start_date)


        if end_date:

            query += """
                AND DATE(s.sale_date) <= %s
            """

            params.append(end_date)


        query += """

            GROUP BY
                c.customer_id,
                c.customer_name

            ORDER BY
                total_spent DESC

            LIMIT %s
        """

        params.append(int(limit))


        cursor.execute(
            query,
            tuple(params)
        )

        return cursor.fetchall()

    finally:

        cursor.close()
        db.close()


# =========================================================
# EMPLOYEE SALES
# =========================================================

def get_employee_sales(
    start_date=None,
    end_date=None,
    limit=10
):

    db = get_connection()
    cursor = db.cursor(dictionary=True)

    try:

        query = """
            SELECT

                e.employee_id,

                e.employee_name,

                COUNT(
                    DISTINCT s.sale_id
                )
                    AS number_of_sales,

                COALESCE(
                    SUM(s.final_amount),
                    0
                )
                    AS total_sales

            FROM sales s

            INNER JOIN employees e
                ON s.employee_id = e.employee_id

            WHERE 1 = 1
        """

        params = []


        if start_date:

            query += """
                AND DATE(s.sale_date) >= %s
            """

            params.append(start_date)


        if end_date:

            query += """
                AND DATE(s.sale_date) <= %s
            """

            params.append(end_date)


        query += """

            GROUP BY
                e.employee_id,
                e.employee_name

            ORDER BY
                total_sales DESC

            LIMIT %s
        """

        params.append(int(limit))


        cursor.execute(
            query,
            tuple(params)
        )

        return cursor.fetchall()

    finally:

        cursor.close()
        db.close()


# =========================================================
# PURCHASE SUMMARY
# =========================================================

def get_purchase_summary(
    start_date=None,
    end_date=None
):

    db = get_connection()
    cursor = db.cursor(dictionary=True)

    try:

        query = """
            SELECT

                COUNT(
                    DISTINCT p.purchase_id
                )
                    AS total_purchases,

                COALESCE(
                    SUM(pi.quantity),
                    0
                )
                    AS total_items_purchased,

                COALESCE(
                    SUM(pi.subtotal),
                    0
                )
                    AS total_purchase_value

            FROM purchases p

            LEFT JOIN purchase_items pi
                ON p.purchase_id = pi.purchase_id

            WHERE 1 = 1
        """

        params = []


        if start_date:

            query += """
                AND DATE(p.purchase_date) >= %s
            """

            params.append(start_date)


        if end_date:

            query += """
                AND DATE(p.purchase_date) <= %s
            """

            params.append(end_date)


        cursor.execute(
            query,
            tuple(params)
        )

        result = cursor.fetchone()


        if result is None:

            return {
                "total_purchases": 0,
                "total_items_purchased": 0,
                "total_purchase_value": 0
            }


        return result

    finally:

        cursor.close()
        db.close()


# =========================================================
# SUPPLIER PURCHASES
# =========================================================

def get_supplier_purchases(
    start_date=None,
    end_date=None,
    limit=10
):

    db = get_connection()
    cursor = db.cursor(dictionary=True)

    try:

        query = """
            SELECT

                s.supplier_id,

                s.supplier_name,

                COUNT(
                    DISTINCT p.purchase_id
                )
                    AS number_of_purchases,

                COALESCE(
                    SUM(p.total_amount),
                    0
                )
                    AS total_purchase_value

            FROM purchases p

            INNER JOIN suppliers s
                ON p.supplier_id = s.supplier_id

            WHERE 1 = 1
        """

        params = []


        if start_date:

            query += """
                AND DATE(p.purchase_date) >= %s
            """

            params.append(start_date)


        if end_date:

            query += """
                AND DATE(p.purchase_date) <= %s
            """

            params.append(end_date)


        query += """

            GROUP BY
                s.supplier_id,
                s.supplier_name

            ORDER BY
                total_purchase_value DESC

            LIMIT %s
        """

        params.append(int(limit))


        cursor.execute(
            query,
            tuple(params)
        )

        return cursor.fetchall()

    finally:

        cursor.close()
        db.close()


# =========================================================
# DAILY PURCHASES
# =========================================================

def get_daily_purchases(
    start_date=None,
    end_date=None
):

    db = get_connection()
    cursor = db.cursor(dictionary=True)

    try:

        query = """
            SELECT

                DATE(p.purchase_date)
                    AS purchase_date,

                COUNT(
                    DISTINCT p.purchase_id
                )
                    AS number_of_purchases,

                COALESCE(
                    SUM(p.total_amount),
                    0
                )
                    AS total_purchases

            FROM purchases p

            WHERE 1 = 1
        """

        params = []


        if start_date:

            query += """
                AND DATE(p.purchase_date) >= %s
            """

            params.append(start_date)


        if end_date:

            query += """
                AND DATE(p.purchase_date) <= %s
            """

            params.append(end_date)


        query += """

            GROUP BY DATE(p.purchase_date)

            ORDER BY DATE(p.purchase_date)
        """


        cursor.execute(
            query,
            tuple(params)
        )

        return cursor.fetchall()

    finally:

        cursor.close()
        db.close()


# =========================================================
# INVENTORY SUMMARY
# =========================================================

def get_inventory_summary():

    db = get_connection()
    cursor = db.cursor(dictionary=True)

    try:

        query = """
            SELECT

                COUNT(*)
                    AS total_products,

                COALESCE(
                    SUM(
                        COALESCE(stock_quantity, 0)
                    ),
                    0
                )
                    AS total_stock,

                COALESCE(
                    SUM(
                        COALESCE(stock_quantity, 0)
                        * purchase_price
                    ),
                    0
                )
                    AS inventory_cost_value,

                COALESCE(
                    SUM(
                        COALESCE(stock_quantity, 0)
                        * selling_price
                    ),
                    0
                )
                    AS inventory_sales_value,

                COALESCE(
                    SUM(
                        CASE

                            WHEN
                                COALESCE(stock_quantity, 0)
                                <= COALESCE(reorder_level, 0)

                            THEN 1

                            ELSE 0

                        END
                    ),
                    0
                )
                    AS low_stock_products,

                COALESCE(
                    SUM(
                        CASE

                            WHEN
                                COALESCE(stock_quantity, 0) = 0

                            THEN 1

                            ELSE 0

                        END
                    ),
                    0
                )
                    AS out_of_stock_products

            FROM products
        """

        cursor.execute(query)

        result = cursor.fetchone()


        if result is None:

            return {
                "total_products": 0,
                "total_stock": 0,
                "inventory_cost_value": 0,
                "inventory_sales_value": 0,
                "low_stock_products": 0,
                "out_of_stock_products": 0
            }


        return result

    finally:

        cursor.close()
        db.close()