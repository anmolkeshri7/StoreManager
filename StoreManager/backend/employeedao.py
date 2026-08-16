from backend.db import get_connection


# =========================================================
# GET ALL EMPLOYEES
# =========================================================

def get_employees():

    db = get_connection()
    cursor = db.cursor(dictionary=True)

    try:

        query = """
            SELECT
                employee_id,
                employee_name,
                phone,
                email,
                role,
                salary,
                joining_date

            FROM employees

            ORDER BY employee_id DESC
        """

        cursor.execute(query)

        return cursor.fetchall()

    finally:

        cursor.close()
        db.close()


# =========================================================
# GET EMPLOYEE BY ID
# =========================================================

def get_employee_by_id(employee_id):

    db = get_connection()
    cursor = db.cursor(dictionary=True)

    try:

        query = """
            SELECT
                employee_id,
                employee_name,
                phone,
                email,
                role,
                salary,
                joining_date

            FROM employees

            WHERE employee_id = %s
        """

        cursor.execute(
            query,
            (employee_id,)
        )

        return cursor.fetchone()

    finally:

        cursor.close()
        db.close()


# =========================================================
# ADD EMPLOYEE
# =========================================================

def add_employee(
    employee_name,
    phone,
    email,
    role,
    salary,
    joining_date
):

    db = get_connection()
    cursor = db.cursor()

    try:

        query = """
            INSERT INTO employees
            (
                employee_name,
                phone,
                email,
                role,
                salary,
                joining_date
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
        """

        cursor.execute(
            query,
            (
                employee_name,
                phone,
                email,
                role,
                salary,
                joining_date
            )
        )

        db.commit()

    except Exception:

        db.rollback()

        raise

    finally:

        cursor.close()
        db.close()


# =========================================================
# UPDATE EMPLOYEE
# =========================================================

def update_employee(
    employee_id,
    employee_name,
    phone,
    email,
    role,
    salary,
    joining_date
):

    db = get_connection()
    cursor = db.cursor()

    try:

        query = """
            UPDATE employees

            SET
                employee_name = %s,
                phone = %s,
                email = %s,
                role = %s,
                salary = %s,
                joining_date = %s

            WHERE employee_id = %s
        """

        cursor.execute(
            query,
            (
                employee_name,
                phone,
                email,
                role,
                salary,
                joining_date,
                employee_id
            )
        )

        db.commit()

    except Exception:

        db.rollback()

        raise

    finally:

        cursor.close()
        db.close()


# =========================================================
# DELETE EMPLOYEE
# =========================================================

def delete_employee(employee_id):

    db = get_connection()
    cursor = db.cursor(dictionary=True)

    try:

        # =================================================
        # CHECK SALES
        # =================================================

        cursor.execute(
            """
            SELECT COUNT(*) AS sales_count

            FROM sales

            WHERE employee_id = %s
            """,
            (employee_id,)
        )

        sales_result = cursor.fetchone()

        sales_count = (
            sales_result["sales_count"] or 0
        )


        # =================================================
        # CHECK PURCHASES
        # =================================================

        cursor.execute(
            """
            SELECT COUNT(*) AS purchase_count

            FROM purchases

            WHERE employee_id = %s
            """,
            (employee_id,)
        )

        purchase_result = cursor.fetchone()

        purchase_count = (
            purchase_result["purchase_count"] or 0
        )


        # =================================================
        # PREVENT DELETE IF LINKED
        # =================================================

        if sales_count > 0 or purchase_count > 0:

            message = (
                "This employee cannot be deleted because "
                "they are linked to existing transactions."
            )

            if sales_count > 0:

                message += (
                    f" Sales records: {sales_count}."
                )

            if purchase_count > 0:

                message += (
                    f" Purchase records: {purchase_count}."
                )

            raise ValueError(message)


        # =================================================
        # DELETE EMPLOYEE
        # =================================================

        cursor.execute(
            """
            DELETE FROM employees

            WHERE employee_id = %s
            """,
            (employee_id,)
        )


        # =================================================
        # CHECK WHETHER EMPLOYEE EXISTED
        # =================================================

        if cursor.rowcount == 0:

            raise ValueError(
                "Employee not found."
            )


        db.commit()


    except Exception:

        db.rollback()

        raise

    finally:

        cursor.close()
        db.close()


# =========================================================
# SEARCH EMPLOYEES
# =========================================================

def search_employees(search_term):

    db = get_connection()
    cursor = db.cursor(dictionary=True)

    try:

        query = """
            SELECT
                employee_id,
                employee_name,
                phone,
                email,
                role,
                salary,
                joining_date

            FROM employees

            WHERE
                employee_name LIKE %s

                OR phone LIKE %s

                OR email LIKE %s

                OR role LIKE %s

            ORDER BY employee_id DESC
        """

        search_pattern = "%" + search_term + "%"

        cursor.execute(
            query,
            (
                search_pattern,
                search_pattern,
                search_pattern,
                search_pattern
            )
        )

        return cursor.fetchall()

    finally:

        cursor.close()
        db.close()