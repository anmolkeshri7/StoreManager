import os

from flask import (
    Flask,
    render_template,
    request,
    redirect,
    url_for,
    flash,
    session
)

from mysql.connector import IntegrityError
from werkzeug.security import check_password_hash

from backend.db import get_connection

from backend.auth import login_required, role_required

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

from backend.reportsdao import (
    get_sales_summary,
    get_profit_summary,
    get_daily_sales,
    get_top_selling_products as get_reports_top_selling_products,
    get_sales_by_category as get_reports_sales_by_category,
    get_customer_sales,
    get_employee_sales,
    get_purchase_summary,
    get_supplier_purchases,
    get_daily_purchases,
    get_inventory_summary
)


# =========================================================
# FLASK APP
# =========================================================

app = Flask(__name__)


# =========================================================
# SECRET KEY
# =========================================================

app.secret_key = os.getenv(
    "FLASK_SECRET_KEY",
    "development-secret-change-this"
)


# =========================================================
# TEMPLATE CONTEXT
# =========================================================
#
# Makes logged-in username and role available in base.html
#
# =========================================================

@app.context_processor
def inject_user_info():

    return {
        "current_username": session.get("username"),
        "current_role": session.get("role")
    }


# =========================================================
# LOGIN
# =========================================================

@app.route(
    "/login",
    methods=["GET", "POST"]
)
def login():

    # Already logged in
    if "user_id" in session:

        return redirect(
            url_for("home")
        )


    if request.method == "POST":

        username = request.form.get(
            "username",
            ""
        ).strip()

        password = request.form.get(
            "password",
            ""
        )


        if not username or not password:

            flash(
                "Please enter your username and password.",
                "danger"
            )

            return render_template(
                "login.html"
            )


        connection = None
        cursor = None

        try:

            connection = get_connection()

            cursor = connection.cursor(
                dictionary=True
            )

            cursor.execute(
                """
                SELECT
                    user_id,
                    username,
                    password,
                    role,
                    employee_id
                FROM users
                WHERE username = %s
                LIMIT 1
                """,
                (username,)
            )

            user = cursor.fetchone()


            if user is None:

                flash(
                    "Invalid username or password.",
                    "danger"
                )

                return render_template(
                    "login.html"
                )


            stored_password = user["password"]


            # =================================================
            # PASSWORD VERIFICATION
            # =================================================

            try:

                password_valid = check_password_hash(
                    stored_password,
                    password
                )

            except ValueError:

                password_valid = False


            if not password_valid:

                flash(
                    "Invalid username or password.",
                    "danger"
                )

                return render_template(
                    "login.html"
                )


            # =================================================
            # LOGIN SUCCESS
            # =================================================

            session.clear()

            session["user_id"] = user["user_id"]
            session["username"] = user["username"]
            session["role"] = user["role"]
            session["employee_id"] = user["employee_id"]


            flash(
                f"Welcome back, {user['username']}!",
                "success"
            )


            return redirect(
                url_for("home")
            )


        except Exception as error:

            print(
                "LOGIN ERROR:",
                error
            )

            flash(
                "Unable to process login right now.",
                "danger"
            )

            return render_template(
                "login.html"
            )


        finally:

            if cursor:

                cursor.close()

            if connection:

                connection.close()


    return render_template(
        "login.html"
    )


# =========================================================
# LOGOUT
# =========================================================

@app.route("/logout")
def logout():

    username = session.get(
        "username"
    )


    session.clear()


    if username:

        flash(
            "You have been logged out successfully.",
            "success"
        )


    return redirect(
        url_for("login")
    )


# =========================================================
# HOME / DASHBOARD
# =========================================================

@app.route("/")
@login_required
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
@role_required(
    "Admin",
    "Manager",
    "Employee"
)
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
@role_required(
    "Admin",
    "Manager"
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


# ---------------------------------------------------------
# EDIT PRODUCT
# ---------------------------------------------------------

@app.route(
    "/products/edit/<int:product_id>",
    methods=["GET", "POST"]
)
@role_required(
    "Admin",
    "Manager"
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


# ---------------------------------------------------------
# DELETE PRODUCT
# ---------------------------------------------------------

@app.route(
    "/products/delete/<int:product_id>",
    methods=["POST"]
)
@role_required(
    "Admin",
    "Manager"
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
@role_required(
    "Admin",
    "Manager",
    "Employee"
)
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
@role_required(
    "Admin",
    "Manager"
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
@role_required(
    "Admin",
    "Manager"
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
@role_required(
    "Admin",
    "Manager"
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
@role_required(
    "Admin",
    "Manager",
    "Employee"
)
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
@role_required(
    "Admin",
    "Manager"
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
@role_required(
    "Admin",
    "Manager"
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
@role_required(
    "Admin",
    "Manager"
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
@role_required(
    "Admin",
    "Manager",
    "Employee"
)
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
@role_required(
    "Admin",
    "Manager",
    "Employee"
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
@role_required(
    "Admin",
    "Manager",
    "Employee"
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
@role_required(
    "Admin",
    "Manager"
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
@role_required("Admin")
def employees():

    search = request.args.get(
        "search",
        ""
    ).strip()


    role = request.args.get(
        "role",
        ""
    ).strip()


    if search:

        data = search_employees(
            search
        )

    else:

        data = get_employees()


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
@role_required("Admin")
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


        joining_date = request.form.get(
            "joining_date"
        )


        if not joining_date:

            joining_date = None


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
@role_required("Admin")
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


        joining_date = request.form.get(
            "joining_date"
        )


        if not joining_date:

            joining_date = None


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
@role_required("Admin")
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
@role_required(
    "Admin",
    "Manager"
)
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
@role_required(
    "Admin",
    "Manager"
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
@role_required(
    "Admin",
    "Manager"
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
@role_required(
    "Admin",
    "Manager"
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
@role_required(
    "Admin",
    "Manager",
    "Employee"
)
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
@role_required(
    "Admin",
    "Manager",
    "Employee"
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
@role_required(
    "Admin",
    "Manager",
    "Employee"
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
@role_required(
    "Admin",
    "Manager"
)
def delete_sale_page(sale_id):

    delete_sale(
        sale_id
    )


    return redirect(
        url_for("sales")
    )


# =========================================================
# REPORTS ROUTES
# =========================================================

@app.route("/reports")
@role_required(
    "Admin",
    "Manager"
)
def reports():

    start_date = request.args.get(
        "start_date",
        ""
    ).strip()


    end_date = request.args.get(
        "end_date",
        ""
    ).strip()


    sales_summary = get_sales_summary(
        start_date or None,
        end_date or None
    )


    profit_summary = get_profit_summary(
        start_date or None,
        end_date or None
    )


    daily_sales = get_daily_sales(
        start_date or None,
        end_date or None
    )


    top_selling_products = (
        get_reports_top_selling_products(
            start_date or None,
            end_date or None
        )
    )


    sales_by_category = (
        get_reports_sales_by_category(
            start_date or None,
            end_date or None
        )
    )


    customer_sales = get_customer_sales(
        start_date or None,
        end_date or None
    )


    employee_sales = get_employee_sales(
        start_date or None,
        end_date or None
    )


    purchase_summary = get_purchase_summary(
        start_date or None,
        end_date or None
    )


    supplier_purchases = get_supplier_purchases(
        start_date or None,
        end_date or None
    )


    daily_purchases = get_daily_purchases(
        start_date or None,
        end_date or None
    )


    inventory_summary = get_inventory_summary()


    return render_template(
        "reports.html",
        start_date=start_date,
        end_date=end_date,
        sales_summary=sales_summary,
        profit_summary=profit_summary,
        daily_sales=daily_sales,
        top_selling_products=top_selling_products,
        sales_by_category=sales_by_category,
        customer_sales=customer_sales,
        employee_sales=employee_sales,
        purchase_summary=purchase_summary,
        supplier_purchases=supplier_purchases,
        daily_purchases=daily_purchases,
        inventory_summary=inventory_summary
    )


# =========================================================
# 403 ERROR
# =========================================================

@app.errorhandler(403)
def forbidden(error):

    return (
        """
        <!DOCTYPE html>

        <html>

        <head>

            <title>
                Access Denied - Store Manager
            </title>

            <meta
                name="viewport"
                content="width=device-width, initial-scale=1.0"
            >

            <style>

                body {
                    margin: 0;
                    padding: 30px;

                    min-height: 100vh;

                    display: flex;
                    align-items: center;
                    justify-content: center;

                    background: #f5f7fb;

                    font-family:
                        Arial,
                        Helvetica,
                        sans-serif;
                }

                .box {
                    max-width: 500px;

                    width: 100%;

                    padding: 40px;

                    text-align: center;

                    background: white;

                    border-radius: 16px;

                    border: 1px solid #e5e7eb;

                    box-shadow:
                        0 15px 40px
                        rgba(15, 23, 42, 0.10);
                }

                .icon {
                    font-size: 55px;

                    margin-bottom: 15px;
                }

                h1 {
                    color: #111827;

                    margin-bottom: 10px;
                }

                p {
                    color: #6b7280;

                    line-height: 1.6;
                }

                a {
                    display: inline-block;

                    margin-top: 20px;

                    padding: 11px 20px;

                    border-radius: 8px;

                    background: #2563eb;

                    color: white;

                    text-decoration: none;

                    font-weight: 600;
                }

                a:hover {
                    background: #1d4ed8;
                }

            </style>

        </head>


        <body>

            <div class="box">

                <div class="icon">
                    🔒
                </div>

                <h1>
                    Access Denied
                </h1>

                <p>
                    You do not have permission to access
                    this page with your current account role.
                </p>

                <a href="/">
                    Back to Dashboard
                </a>

            </div>

        </body>

        </html>
        """,
        403
    )


# =========================================================
# RUN APPLICATION
# =========================================================

if __name__ == "__main__":

    app.run(
        host="0.0.0.0",
        port=5000,
        debug=True
    )