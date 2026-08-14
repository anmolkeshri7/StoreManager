from flask import Flask, render_template, request, redirect, url_for

from backend.productsdao import (
    get_products,
    add_product
)

from backend.categorydao import get_categories
from backend.supplierdao import get_suppliers


app = Flask(__name__)


# ================= HOME =================

@app.route("/")
def home():

    return "Store Management System"


# ================= PRODUCTS =================

@app.route("/products")
def products():

    data = get_products()

    return render_template(
        "products.html",
        products=data
    )


# ================= ADD PRODUCT =================

@app.route("/products/add", methods=["GET", "POST"])
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
            supplier_id = int(supplier_id)
        else:
            supplier_id = None

        barcode = request.form.get("barcode")

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


# ================= RUN =================

if __name__ == "__main__":

    app.run(debug=True)