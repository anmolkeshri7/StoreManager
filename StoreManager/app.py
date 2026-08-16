from flask import Flask, render_template, request, redirect, url_for
from mysql.connector import IntegrityError


# =========================================================
# DAO IMPORTS
# =========================================================

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

from backend.employeedao import (
    get_employees,
    get_employee_by_id,
    add_employee,
    update_employee,
    delete_employee,
    search_employees
)

from backend.purchasedao import (
    get_purchases,
    get_purchase_by_id,
    get_purchase_details,
    create_purchase,
    delete_purchase
)

from backend.salesdao import (
    get_sales,
    get_sale_by_id,
    get_sale_details,
    get_sale_payments,
    create_sale,
    delete_sale
)

from backend.dashboarddao import (
    get_dashboard_stats,
    get_recent_sales,
    get_low_stock_products,
    get_top_selling_products,
    get_monthly_sales,
    get_sales_by_category
)


# =========================================================
# FLASK APP
# =========================================================

app = Flask(__name__)


# =========================================================
# HOME / DASHBOARD
# =========================================================

@app.route("/")
def home():

    stats = get_dashboard_stats()

    recent_sales = get_recent_sales()

    low_stock_products = get_low_stock_products()

    top_selling_products = get_top_selling_products()

    monthly_sales = get_monthly_sales()

    sales_by_category = get_sales_by_category()

    return render_template(
        "dashboard.html",
        stats=stats,
        recent_sales=recent_sales,
        low_stock_products=low_stock_products,
        top_selling_products=top_selling_products,
        monthly_sales=monthly_sales,
        sales_by_category=sales_by_category
    )


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


# ---------------------------------------------------------
# ADD PRODUCT
# ---------------------------------------------------------

@app.route(
    "/products/add",
    methods=["GET", "POST"]
)
def add_product_page():

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


# ---------------------------------------------------------
# EDIT PRODUCT
# ---------------------------------------------------------

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


# ---------------------------------------------------------
# DELETE PRODUCT
# ---------------------------------------------------------

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
# CATEGORY ROUTES
# =========================================================

@app.route("/categories")
def categories():

    data = get_categories()

    return render_template(
        "categories.html",
        categories=data
    )


# ---------------------------------------------------------
# ADD CATEGORY
# ---------------------------------------------------------

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


# ---------------------------------------------------------
# EDIT CATEGORY
# ---------------------------------------------------------

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


# ---------------------------------------------------------
# DELETE CATEGORY
# ---------------------------------------------------------

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
            "one or more products are using it.",
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


# ---------------------------------------------------------
# ADD SUPPLIER
# ---------------------------------------------------------

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


# ---------------------------------------------------------
# EDIT SUPPLIER
# ---------------------------------------------------------

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


# ---------------------------------------------------------
# DELETE SUPPLIER
# ---------------------------------------------------------

@app.route(
    "/suppliers/delete/<int:supplier_id>",
    methods=["POST"]
)
def delete_supplier_page(supplier_id):

    try:

        delete_supplier(
            supplier_id
        )

        return redirect(
            url_for("suppliers")
        )

    except IntegrityError:

        return (
            "Cannot delete this supplier because "
            "one or more products are using it.",
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


# ---------------------------------------------------------
# ADD CUSTOMER
# ---------------------------------------------------------

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


# ---------------------------------------------------------
# EDIT CUSTOMER
# ---------------------------------------------------------

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


# ---------------------------------------------------------
# DELETE CUSTOMER
# ---------------------------------------------------------

@app.route(
    "/customers/delete/<int:customer_id>",
    methods=["POST"]
)
def delete_customer_page(customer_id):

    try:

        delete_customer(
            customer_id
        )

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
# EMPLOYEE ROUTES
# =========================================================

@app.route("/employees")
def employees():

    search = request.args.get(
        "search",
        ""
    ).strip()

    role = request.args.get(
        "role",
        ""
    ).strip()


    # =====================================================
    # GET EMPLOYEES
    # =====================================================

    if search:

        data = search_employees(
            search
        )

    else:

        data = get_employees()


    # =====================================================
    # ROLE FILTER
    # =====================================================

    if role:

        data = [
            employee
            for employee in data
            if (employee["role"] or "").lower()
            == role.lower()
        ]


    return render_template(
        "employees.html",
        employees=data,
        search=search,
        selected_role=role
    )


# ---------------------------------------------------------
# ADD EMPLOYEE
# ---------------------------------------------------------

@app.route(
    "/employees/add",
    methods=["GET", "POST"]
)
def add_employee_page():

    if request.method == "POST":

        employee_name = request.form[
            "employee_name"
        ].strip()

        phone = request.form.get(
            "phone",
            ""
        ).strip()

        email = request.form.get(
            "email",
            ""
        ).strip()

        role = request.form.get(
            "role",
            ""
        ).strip()

        salary_text = request.form.get(
            "salary",
            "0"
        ).strip()


        # Empty date → None
        joining_date = request.form.get(
            "joining_date"
        )

        if not joining_date:

            joining_date = None


        # Salary

        if salary_text:

            salary = float(
                salary_text
            )

        else:

            salary = 0


        add_employee(
            employee_name,
            phone,
            email,
            role,
            salary,
            joining_date
        )

        return redirect(
            url_for("employees")
        )


    return render_template(
        "add_employee.html"
    )


# ---------------------------------------------------------
# EDIT EMPLOYEE
# ---------------------------------------------------------

@app.route(
    "/employees/edit/<int:employee_id>",
    methods=["GET", "POST"]
)
def edit_employee_page(employee_id):

    employee = get_employee_by_id(
        employee_id
    )


    if employee is None:

        return "Employee not found", 404


    if request.method == "POST":

        employee_name = request.form[
            "employee_name"
        ].strip()

        phone = request.form.get(
            "phone",
            ""
        ).strip()

        email = request.form.get(
            "email",
            ""
        ).strip()

        role = request.form.get(
            "role",
            ""
        ).strip()

        salary_text = request.form.get(
            "salary",
            "0"
        ).strip()


        # Empty date → None

        joining_date = request.form.get(
            "joining_date"
        )

        if not joining_date:

            joining_date = None


        # Salary

        if salary_text:

            salary = float(
                salary_text
            )

        else:

            salary = 0


        update_employee(
            employee_id,
            employee_name,
            phone,
            email,
            role,
            salary,
            joining_date
        )

        return redirect(
            url_for("employees")
        )


    return render_template(
        "edit_employee.html",
        employee=employee
    )


# ---------------------------------------------------------
# DELETE EMPLOYEE
# ---------------------------------------------------------

@app.route(
    "/employees/delete/<int:employee_id>",
    methods=["POST"]
)
def delete_employee_page(employee_id):

    try:

        delete_employee(
            employee_id
        )

        return redirect(
            url_for("employees")
        )


    except ValueError as error:

        return (
            f"""
            <div style="
                font-family: Arial;
                max-width: 700px;
                margin: 80px auto;
                padding: 30px;
                text-align: center;
            ">

                <h2 style="color: #dc3545;">
                    ⚠️ Employee Cannot Be Deleted
                </h2>

                <p>
                    {error}
                </p>

                <br>

                <a
                    href="/employees"
                    style="
                        display: inline-block;
                        padding: 10px 20px;
                        background: #007bff;
                        color: white;
                        text-decoration: none;
                        border-radius: 6px;
                    "
                >
                    ← Back to Employees
                </a>

            </div>
            """,
            400
        )


    except IntegrityError:

        return (
            """
            <div style="
                font-family: Arial;
                max-width: 700px;
                margin: 80px auto;
                padding: 30px;
                text-align: center;
            ">

                <h2 style="color: #dc3545;">
                    ⚠️ Employee Cannot Be Deleted
                </h2>

                <p>
                    This employee is linked to existing
                    records and cannot be deleted.
                </p>

                <br>

                <a
                    href="/employees"
                    style="
                        display: inline-block;
                        padding: 10px 20px;
                        background: #007bff;
                        color: white;
                        text-decoration: none;
                        border-radius: 6px;
                    "
                >
                    ← Back to Employees
                </a>

            </div>
            """,
            400
        )


# =========================================================
# PURCHASE ROUTES
# =========================================================

@app.route("/purchases")
def purchases():

    data = get_purchases()

    return render_template(
        "purchases.html",
        purchases=data
    )


# ---------------------------------------------------------
# PURCHASE DETAILS
# ---------------------------------------------------------

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


# ---------------------------------------------------------
# ADD PURCHASE
# ---------------------------------------------------------

@app.route(
    "/purchases/add",
    methods=["GET", "POST"]
)
def add_purchase_page():

    suppliers = get_suppliers()

    products = get_products()

    employees = get_employees()


    if request.method == "POST":

        supplier_id = int(
            request.form["supplier_id"]
        )


        employee_id = request.form.get(
            "employee_id"
        )


        if employee_id:

            employee_id = int(
                employee_id
            )

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
                    "product_id":
                        int(product_ids[i]),

                    "quantity":
                        quantity,

                    "purchase_price":
                        purchase_price
                }
            )


        if not items:

            return (
                "Please add at least one valid product.",
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
        products=products,
        employees=employees
    )


# ---------------------------------------------------------
# DELETE PURCHASE
# ---------------------------------------------------------

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
# SALES ROUTES
# =========================================================

@app.route("/sales")
def sales():

    data = get_sales()

    return render_template(
        "sales.html",
        sales=data
    )


# ---------------------------------------------------------
# SALE DETAILS
# ---------------------------------------------------------

@app.route(
    "/sales/<int:sale_id>"
)
def sale_details(sale_id):

    sale = get_sale_by_id(
        sale_id
    )

    if sale is None:

        return "Sale not found", 404


    details = get_sale_details(
        sale_id
    )


    payments = get_sale_payments(
        sale_id
    )


    return render_template(
        "sale_details.html",
        sale=sale,
        details=details,
        payments=payments
    )


# ---------------------------------------------------------
# ADD SALE
# ---------------------------------------------------------

@app.route(
    "/sales/add",
    methods=["GET", "POST"]
)
def add_sale_page():

    customers = get_customers()

    products = get_products()

    employees = get_employees()


    if request.method == "POST":

        customer_id = request.form.get(
            "customer_id"
        )


        if customer_id:

            customer_id = int(
                customer_id
            )

        else:

            customer_id = None


        employee_id = request.form.get(
            "employee_id"
        )


        if employee_id:

            employee_id = int(
                employee_id
            )

        else:

            employee_id = None


        product_ids = request.form.getlist(
            "product_id[]"
        )

        quantities = request.form.getlist(
            "quantity[]"
        )

        selling_prices = request.form.getlist(
            "selling_price[]"
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

            selling_price = float(
                selling_prices[i]
            )


            if quantity <= 0:

                continue


            if selling_price < 0:

                continue


            items.append(
                {
                    "product_id":
                        int(product_ids[i]),

                    "quantity":
                        quantity,

                    "selling_price":
                        selling_price
                }
            )


        if not items:

            return (
                "Please add at least one valid product.",
                400
            )


        discount = float(
            request.form.get(
                "discount",
                0
            )
        )


        tax = float(
            request.form.get(
                "tax",
                0
            )
        )


        payment_amount = float(
            request.form.get(
                "payment_amount",
                0
            )
        )


        payment_method = request.form.get(
            "payment_method"
        )


        if discount < 0:

            discount = 0


        if tax < 0:

            tax = 0


        if payment_amount < 0:

            payment_amount = 0


        if not payment_method:

            return (
                "Please select a payment method.",
                400
            )


        try:

            create_sale(
                customer_id,
                employee_id,
                items,
                discount,
                tax,
                payment_amount,
                payment_method
            )


        except ValueError as error:

            return str(error), 400


        return redirect(
            url_for("sales")
        )


    return render_template(
        "add_sale.html",
        customers=customers,
        products=products,
        employees=employees
    )


# ---------------------------------------------------------
# DELETE SALE
# ---------------------------------------------------------

@app.route(
    "/sales/delete/<int:sale_id>",
    methods=["POST"]
)
def delete_sale_page(sale_id):

    delete_sale(
        sale_id
    )

    return redirect(
        url_for("sales")
    )


# =========================================================
# RUN APPLICATION
# =========================================================

if __name__ == "__main__":

    app.run(
        debug=True
    )