from backend.db import get_connection


# =========================================================
# GET ALL CATEGORIES
# =========================================================

def get_categories():

    db = get_connection()

    cursor = db.cursor(dictionary=True)

    query = """
        SELECT
            category_id,
            category_name,
            description
        FROM categories
        ORDER BY category_id DESC
    """

    cursor.execute(query)

    categories = cursor.fetchall()

    cursor.close()

    db.close()

    return categories


# =========================================================
# GET CATEGORY BY ID
# =========================================================

def get_category_by_id(category_id):

    db = get_connection()

    cursor = db.cursor(dictionary=True)

    query = """
        SELECT
            category_id,
            category_name,
            description
        FROM categories
        WHERE category_id = %s
    """

    cursor.execute(
        query,
        (category_id,)
    )

    category = cursor.fetchone()

    cursor.close()

    db.close()

    return category


# =========================================================
# ADD CATEGORY
# =========================================================

def add_category(
    category_name,
    description
):

    db = get_connection()

    cursor = db.cursor()

    query = """
        INSERT INTO categories
        (
            category_name,
            description
        )
        VALUES
        (
            %s,
            %s
        )
    """

    values = (
        category_name,
        description
    )

    cursor.execute(
        query,
        values
    )

    db.commit()

    cursor.close()

    db.close()


# =========================================================
# UPDATE CATEGORY
# =========================================================

def update_category(
    category_id,
    category_name,
    description
):

    db = get_connection()

    cursor = db.cursor()

    query = """
        UPDATE categories

        SET
            category_name = %s,
            description = %s

        WHERE category_id = %s
    """

    values = (
        category_name,
        description,
        category_id
    )

    cursor.execute(
        query,
        values
    )

    db.commit()

    cursor.close()

    db.close()


# =========================================================
# DELETE CATEGORY
# =========================================================

def delete_category(category_id):

    db = get_connection()

    cursor = db.cursor()

    query = """
        DELETE FROM categories
        WHERE category_id = %s
    """

    cursor.execute(
        query,
        (category_id,)
    )

    db.commit()

    cursor.close()

    db.close()