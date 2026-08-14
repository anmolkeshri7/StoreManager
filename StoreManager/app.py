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

from backend.supplierdao import (
    get_suppliers,
    get_supplier_by_id,
    add_supplier,
    update_supplier,
    delete_supplier
)

from backend.customerdao import (
    get_customers,
    get_customer_by_id,
    add_customer,
    update_customer,
    delete_customer
)

from backend.purchasedao import (
    get_purchases,
    get_purchase_by_id,
    get_purchase_details,
    create_purchase,
    delete_purchase
)


app = Flask(__name__)


# =========================================================
# HOME
# =========================================================

@app.route("/")
def home():

    return "Store Management System"


# =========================================================
# PRODUCT ROUTES
# =========================================================

@app.route("/products")
def products():

    data = get_products()

    return render_template(
        "products.html",
        products=data
    )


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


@app.route(
    "/products/delete/<int:product_id>",
    methods=["POST"]
)
def delete_product_page(product_id):

    delete_product(product_id)

    return redirect(
        url_for("products")
    )


# =========================================================
# CATEGORY ROUTES
# =========================================================

@app.route("/categories")
def categories():

    data = get_categories()

    return render_template(
        "categories.html",
        categories=data
    )


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


@app.route(
    "/categories/delete/<int:category_id>",
    methods=["POST"]
)
def delete_category_page(category_id):

    try:

        delete_category(category_id)

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
# SUPPLIER ROUTES
# =========================================================

@app.route("/suppliers")
def suppliers():

    data = get_suppliers()

    return render_template(
        "suppliers.html",
        suppliers=data
    )


@app.route(
    "/suppliers/add",
    methods=["GET", "POST"]
)
def add_supplier_page():

    if request.method == "POST":

        supplier_name = request.form[
            "supplier_name"
        ].strip()

        phone = request.form.get(
            "phone",
            ""
        ).strip()

        email = request.form.get(
            "email",
            ""
        ).strip()

        address = request.form.get(
            "address",
            ""
        ).strip()

        add_supplier(
            supplier_name,
            phone,
            email,
            address
        )

        return redirect(
            url_for("suppliers")
        )

    return render_template(
        "add_supplier.html"
    )


@app.route(
    "/suppliers/edit/<int:supplier_id>",
    methods=["GET", "POST"]
)
def edit_supplier_page(supplier_id):

    supplier = get_supplier_by_id(
        supplier_id
    )

    if supplier is None:
        return "Supplier not found", 404

    if request.method == "POST":

        supplier_name = request.form[
            "supplier_name"
        ].strip()

        phone = request.form.get(
            "phone",
            ""
        ).strip()

        email = request.form.get(
            "email",
            ""
        ).strip()

        address = request.form.get(
            "address",
            ""
        ).strip()

        update_supplier(
            supplier_id,
            supplier_name,
            phone,
            email,
            address
        )

        return redirect(
            url_for("suppliers")
        )

    return render_template(
        "edit_supplier.html",
        supplier=supplier
    )


@app.route(
    "/suppliers/delete/<int:supplier_id>",
    methods=["POST"]
)
def delete_supplier_page(supplier_id):

    try:

        delete_supplier(supplier_id)

        return redirect(
            url_for("suppliers")
        )

    except IntegrityError:

        return (
            "Cannot delete this supplier because "
            "one or more products are using it. "
            "Change the products to another supplier "
            "before deleting this supplier.",
            400
        )


# =========================================================
# CUSTOMER ROUTES
# =========================================================

@app.route("/customers")
def customers():

    data = get_customers()

    return render_template(
        "customers.html",
        customers=data
    )


@app.route(
    "/customers/add",
    methods=["GET", "POST"]
)
def add_customer_page():

    if request.method == "POST":

        customer_name = request.form[
            "customer_name"
        ].strip()

        phone = request.form.get(
            "phone",
            ""
        ).strip()

        email = request.form.get(
            "email",
            ""
        ).strip()

        address = request.form.get(
            "address",
            ""
        ).strip()

        add_customer(
            customer_name,
            phone,
            email,
            address
        )

        return redirect(
            url_for("customers")
        )

    return render_template(
        "add_customer.html"
    )


@app.route(
    "/customers/edit/<int:customer_id>",
    methods=["GET", "POST"]
)
def edit_customer_page(customer_id):

    customer = get_customer_by_id(
        customer_id
    )

    if customer is None:
        return "Customer not found", 404

    if request.method == "POST":

        customer_name = request.form[
            "customer_name"
        ].strip()

        phone = request.form.get(
            "phone",
            ""
        ).strip()

        email = request.form.get(
            "email",
            ""
        ).strip()

        address = request.form.get(
            "address",
            ""
        ).strip()

        update_customer(
            customer_id,
            customer_name,
            phone,
            email,
            address
        )

        return redirect(
            url_for("customers")
        )

    return render_template(
        "edit_customer.html",
        customer=customer
    )


@app.route(
    "/customers/delete/<int:customer_id>",
    methods=["POST"]
)
def delete_customer_page(customer_id):

    try:

        delete_customer(customer_id)

        return redirect(
            url_for("customers")
        )

    except IntegrityError:

        return (
            "Cannot delete this customer because "
            "this customer has existing sales records.",
            400
        )


# =========================================================
# PURCHASE ROUTES
# =========================================================

# ---------------- VIEW PURCHASES ----------------

@app.route("/purchases")
def purchases():

    data = get_purchases()

    return render_template(
        "purchases.html",
        purchases=data
    )


# ---------------- VIEW PURCHASE DETAILS ----------------

@app.route(
    "/purchases/<int:purchase_id>"
)
def purchase_details(purchase_id):

    purchase = get_purchase_by_id(
        purchase_id
    )

    if purchase is None:
        return "Purchase not found", 404

    details = get_purchase_details(
        purchase_id
    )

    return render_template(
        "purchase_details.html",
        purchase=purchase,
        details=details
    )


# ---------------- ADD PURCHASE ----------------

@app.route(
    "/purchases/add",
    methods=["GET", "POST"]
)
def add_purchase_page():

    suppliers = get_suppliers()

    products = get_products()


    if request.method == "POST":

        supplier_id = int(
            request.form["supplier_id"]
        )

        employee_id = request.form.get(
            "employee_id"
        )

        if employee_id:
            employee_id = int(employee_id)
        else:
            employee_id = None


        product_ids = request.form.getlist(
            "product_id[]"
        )

        quantities = request.form.getlist(
            "quantity[]"
        )

        purchase_prices = request.form.getlist(
            "purchase_price[]"
        )


        items = []


        for i in range(
            len(product_ids)
        ):

            if not product_ids[i]:
                continue

            quantity = int(
                quantities[i]
            )

            purchase_price = float(
                purchase_prices[i]
            )


            if quantity <= 0:
                continue


            if purchase_price < 0:
                continue


            items.append(
                {
                    "product_id": int(
                        product_ids[i]
                    ),

                    "quantity": quantity,

                    "purchase_price":
                        purchase_price
                }
            )


        if not items:

            return (
                "Please add at least one "
                "valid product.",
                400
            )


        create_purchase(
            supplier_id,
            employee_id,
            items
        )


        return redirect(
            url_for("purchases")
        )


    return render_template(
        "add_purchase.html",
        suppliers=suppliers,
        products=products
    )


# ---------------- DELETE PURCHASE ----------------

@app.route(
    "/purchases/delete/<int:purchase_id>",
    methods=["POST"]
)
def delete_purchase_page(purchase_id):

    delete_purchase(
        purchase_id
    )

    return redirect(
        url_for("purchases")
    )


# =========================================================
# RUN APPLICATION
# =========================================================

if __name__ == "__main__":

    app.run(
        debug=True
    )