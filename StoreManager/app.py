from flask import Flask, render_template, request, redirect, url_for

from mysql.connector import IntegrityError


from backend.productsdao import (
    get_products,
    add_product,
    get_product_by_id,
    update_product,
    delete_product
)


from backend.categorydao import (
    get_categories,
    get_category_by_id,
    add_category,
    update_category,
    delete_category
)


from backend.supplierdao import get_suppliers


app = Flask(__name__)


# =========================================================
# HOME
# =========================================================

@app.route("/")
def home():

    return "Store Management System"


# =========================================================
# PRODUCTS
# =========================================================


@app.route("/products")
def products():

    data = get_products()

    return render_template(
        "products.html",
        products=data
    )


# =========================================================
# ADD PRODUCT
# =========================================================

@app.route(
    "/products/add",
    methods=["GET", "POST"]
)
def add_product_page():

    categories = get_categories()

    suppliers = get_suppliers()


    if request.method == "POST":

        product_name = request.form["product_name"]

        category_id = int(
            request.form["category_id"]
        )

        supplier_id = request.form.get(
            "supplier_id"
        )


        if supplier_id:

            supplier_id = int(
                supplier_id
            )

        else:

            supplier_id = None


        barcode = request.form.get(
            "barcode"
        )


        purchase_price = float(
            request.form["purchase_price"]
        )


        selling_price = float(
            request.form["selling_price"]
        )


        stock_quantity = int(
            request.form["stock_quantity"]
        )


        reorder_level = int(
            request.form["reorder_level"]
        )


        unit = request.form["unit"]


        add_product(
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


        return redirect(
            url_for("products")
        )


    return render_template(
        "add_product.html",
        categories=categories,
        suppliers=suppliers
    )


# =========================================================
# EDIT PRODUCT
# =========================================================

@app.route(
    "/products/edit/<int:product_id>",
    methods=["GET", "POST"]
)
def edit_product_page(product_id):

    product = get_product_by_id(
        product_id
    )


    if product is None:

        return "Product not found", 404


    categories = get_categories()

    suppliers = get_suppliers()


    if request.method == "POST":

        product_name = request.form[
            "product_name"
        ]


        category_id = int(
            request.form["category_id"]
        )


        supplier_id = request.form.get(
            "supplier_id"
        )


        if supplier_id:

            supplier_id = int(
                supplier_id
            )

        else:

            supplier_id = None


        barcode = request.form.get(
            "barcode"
        )


        purchase_price = float(
            request.form["purchase_price"]
        )


        selling_price = float(
            request.form["selling_price"]
        )


        stock_quantity = int(
            request.form["stock_quantity"]
        )


        reorder_level = int(
            request.form["reorder_level"]
        )


        unit = request.form["unit"]


        update_product(
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
        )


        return redirect(
            url_for("products")
        )


    return render_template(
        "edit_product.html",
        product=product,
        categories=categories,
        suppliers=suppliers
    )


# =========================================================
# DELETE PRODUCT
# =========================================================

@app.route(
    "/products/delete/<int:product_id>",
    methods=["POST"]
)
def delete_product_page(product_id):

    delete_product(
        product_id
    )

    return redirect(
        url_for("products")
    )


# =========================================================
# CATEGORIES
# =========================================================


@app.route("/categories")
def categories():

    data = get_categories()

    return render_template(
        "categories.html",
        categories=data
    )


# =========================================================
# ADD CATEGORY
# =========================================================

@app.route(
    "/categories/add",
    methods=["GET", "POST"]
)
def add_category_page():

    if request.method == "POST":

        category_name = request.form[
            "category_name"
        ].strip()


        description = request.form.get(
            "description",
            ""
        ).strip()


        add_category(
            category_name,
            description
        )


        return redirect(
            url_for("categories")
        )


    return render_template(
        "add_category.html"
    )


# =========================================================
# EDIT CATEGORY
# =========================================================

@app.route(
    "/categories/edit/<int:category_id>",
    methods=["GET", "POST"]
)
def edit_category_page(category_id):

    category = get_category_by_id(
        category_id
    )


    if category is None:

        return "Category not found", 404


    if request.method == "POST":

        category_name = request.form[
            "category_name"
        ].strip()


        description = request.form.get(
            "description",
            ""
        ).strip()


        update_category(
            category_id,
            category_name,
            description
        )


        return redirect(
            url_for("categories")
        )


    return render_template(
        "edit_category.html",
        category=category
    )


# =========================================================
# DELETE CATEGORY
# =========================================================

@app.route(
    "/categories/delete/<int:category_id>",
    methods=["POST"]
)
def delete_category_page(category_id):

    try:

        delete_category(
            category_id
        )


        return redirect(
            url_for("categories")
        )


    except IntegrityError:

        return (
            "Cannot delete this category because "
            "one or more products are using it. "
            "Change the products to another category "
            "before deleting this category.",
            400
        )


# =========================================================
# RUN APPLICATION
# =========================================================

if __name__ == "__main__":

    app.run(
        debug=True
    )