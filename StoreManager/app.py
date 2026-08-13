from flask import Flask, render_template
from backend.productsdao import get_products

app = Flask(__name__)


@app.route("/")
def home():
    return "Store Management System"


@app.route("/products")
def products():
    data = get_products()

    return render_template(
        "products.html",
        products=data
    )


if __name__ == "__main__":
    app.run(debug=True)