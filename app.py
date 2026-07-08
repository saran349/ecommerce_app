"""
app.py — E-Commerce Website
Skills demonstrated: Python, Flask, REST API, MySQL (via mysql-connector),
CRUD operations, HTML5/CSS3/JavaScript, OOP-style route organization, SDLC practices.
"""
from functools import wraps
from flask import Flask, render_template, request, redirect, url_for, session, jsonify, flash
from werkzeug.security import generate_password_hash, check_password_hash

import db

app = Flask(__name__)
app.secret_key = "change-this-to-a-random-secret-key"  # required for sessions


# ---------------------------------------------------------------
# Helpers / decorators
# ---------------------------------------------------------------
def login_required(view):
    @wraps(view)
    def wrapped(*args, **kwargs):
        if "user_id" not in session:
            flash("Please log in to continue.", "warning")
            return redirect(url_for("login"))
        return view(*args, **kwargs)
    return wrapped


def current_user_id():
    return session.get("user_id")


# ---------------------------------------------------------------
# Auth routes
# ---------------------------------------------------------------
@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        full_name = request.form["full_name"].strip()
        email = request.form["email"].strip().lower()
        password = request.form["password"]

        existing = db.fetch_one("SELECT id FROM users WHERE email = %s", (email,))
        if existing:
            flash("An account with that email already exists.", "danger")
            return redirect(url_for("register"))

        password_hash = generate_password_hash(password)
        db.execute(
            "INSERT INTO users (full_name, email, password_hash) VALUES (%s, %s, %s)",
            (full_name, email, password_hash),
        )
        flash("Account created! Please log in.", "success")
        return redirect(url_for("login"))

    return render_template("register.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form["email"].strip().lower()
        password = request.form["password"]

        user = db.fetch_one("SELECT * FROM users WHERE email = %s", (email,))
        if user and check_password_hash(user["password_hash"], password):
            session["user_id"] = user["id"]
            session["full_name"] = user["full_name"]
            flash(f"Welcome back, {user['full_name']}!", "success")
            return redirect(url_for("index"))

        flash("Invalid email or password.", "danger")
        return redirect(url_for("login"))

    return render_template("login.html")


@app.route("/logout")
def logout():
    session.clear()
    flash("You have been logged out.", "success")
    return redirect(url_for("index"))


# ---------------------------------------------------------------
# Page routes (server-rendered with Jinja — HTML5/CSS3 frontend)
# ---------------------------------------------------------------
@app.route("/")
def index():
    category = request.args.get("category")
    if category:
        products = db.fetch_all(
            "SELECT * FROM products WHERE category = %s ORDER BY created_at DESC", (category,)
        )
    else:
        products = db.fetch_all("SELECT * FROM products ORDER BY created_at DESC")

    categories = db.fetch_all("SELECT DISTINCT category FROM products ORDER BY category")
    return render_template("index.html", products=products, categories=categories, active_category=category)


@app.route("/product/<int:product_id>")
def product_detail(product_id):
    product = db.fetch_one("SELECT * FROM products WHERE id = %s", (product_id,))
    if not product:
        flash("Product not found.", "danger")
        return redirect(url_for("index"))
    return render_template("product.html", product=product)


@app.route("/cart")
@login_required
def cart_page():
    items = db.fetch_all(
        """SELECT ci.id, ci.quantity, p.id AS product_id, p.name, p.price, p.image_url,
                  (ci.quantity * p.price) AS subtotal
           FROM cart_items ci
           JOIN products p ON p.id = ci.product_id
           WHERE ci.user_id = %s""",
        (current_user_id(),),
    )
    total = sum(item["subtotal"] for item in items)
    return render_template("cart.html", items=items, total=total)


@app.route("/checkout", methods=["GET", "POST"])
@login_required
def checkout():
    items = db.fetch_all(
        """SELECT ci.quantity, p.id AS product_id, p.name, p.price, p.stock,
                  (ci.quantity * p.price) AS subtotal
           FROM cart_items ci
           JOIN products p ON p.id = ci.product_id
           WHERE ci.user_id = %s""",
        (current_user_id(),),
    )

    if not items:
        flash("Your cart is empty.", "warning")
        return redirect(url_for("cart_page"))

    total = sum(item["subtotal"] for item in items)

    if request.method == "POST":
        address = request.form["address"].strip()

        # Create order (CRUD: Create)
        order_id, _ = db.execute(
            "INSERT INTO orders (user_id, total_amount, shipping_address) VALUES (%s, %s, %s)",
            (current_user_id(), total, address),
        )

        # Create order_items and decrement stock
        for item in items:
            db.execute(
                "INSERT INTO order_items (order_id, product_id, quantity, unit_price) VALUES (%s, %s, %s, %s)",
                (order_id, item["product_id"], item["quantity"], item["price"]),
            )
            db.execute(
                "UPDATE products SET stock = stock - %s WHERE id = %s",
                (item["quantity"], item["product_id"]),
            )

        # Clear the cart (CRUD: Delete)
        db.execute("DELETE FROM cart_items WHERE user_id = %s", (current_user_id(),))

        flash("Order placed successfully!", "success")
        return redirect(url_for("order_history"))

    return render_template("checkout.html", items=items, total=total)


@app.route("/orders")
@login_required
def order_history():
    orders = db.fetch_all(
        "SELECT * FROM orders WHERE user_id = %s ORDER BY created_at DESC", (current_user_id(),)
    )
    for order in orders:
        order["items"] = db.fetch_all(
            """SELECT oi.quantity, oi.unit_price, p.name
               FROM order_items oi JOIN products p ON p.id = oi.product_id
               WHERE oi.order_id = %s""",
            (order["id"],),
        )
    return render_template("orders.html", orders=orders)


# =================================================================
# REST API — used by static/js/main.js for add/update/remove-from-cart
# without a full page reload. Demonstrates REST + CRUD + JSON responses.
# =================================================================

@app.route("/api/products", methods=["GET"])
def api_list_products():
    products = db.fetch_all("SELECT * FROM products ORDER BY created_at DESC")
    return jsonify(products), 200


@app.route("/api/products/<int:product_id>", methods=["GET"])
def api_get_product(product_id):
    product = db.fetch_one("SELECT * FROM products WHERE id = %s", (product_id,))
    if not product:
        return jsonify({"error": "Product not found"}), 404
    return jsonify(product), 200


@app.route("/api/cart", methods=["GET"])
@login_required
def api_get_cart():
    items = db.fetch_all(
        """SELECT ci.id, ci.quantity, p.id AS product_id, p.name, p.price,
                  (ci.quantity * p.price) AS subtotal
           FROM cart_items ci JOIN products p ON p.id = ci.product_id
           WHERE ci.user_id = %s""",
        (current_user_id(),),
    )
    return jsonify(items), 200


@app.route("/api/cart", methods=["POST"])
@login_required
def api_add_to_cart():
    data = request.get_json(force=True)
    product_id = data.get("product_id")
    quantity = int(data.get("quantity", 1))

    if not product_id or quantity < 1:
        return jsonify({"error": "product_id and a valid quantity are required"}), 400

    product = db.fetch_one("SELECT id, stock FROM products WHERE id = %s", (product_id,))
    if not product:
        return jsonify({"error": "Product not found"}), 404
    if quantity > product["stock"]:
        return jsonify({"error": "Requested quantity exceeds available stock"}), 400

    existing = db.fetch_one(
        "SELECT * FROM cart_items WHERE user_id = %s AND product_id = %s",
        (current_user_id(), product_id),
    )
    if existing:
        db.execute(
            "UPDATE cart_items SET quantity = quantity + %s WHERE id = %s",
            (quantity, existing["id"]),
        )
    else:
        db.execute(
            "INSERT INTO cart_items (user_id, product_id, quantity) VALUES (%s, %s, %s)",
            (current_user_id(), product_id, quantity),
        )

    return jsonify({"message": "Added to cart"}), 201


@app.route("/api/cart/<int:item_id>", methods=["PUT"])
@login_required
def api_update_cart_item(item_id):
    data = request.get_json(force=True)
    quantity = int(data.get("quantity", 1))

    item = db.fetch_one(
        "SELECT * FROM cart_items WHERE id = %s AND user_id = %s", (item_id, current_user_id())
    )
    if not item:
        return jsonify({"error": "Cart item not found"}), 404

    if quantity < 1:
        db.execute("DELETE FROM cart_items WHERE id = %s", (item_id,))
        return jsonify({"message": "Item removed"}), 200

    db.execute("UPDATE cart_items SET quantity = %s WHERE id = %s", (quantity, item_id))
    return jsonify({"message": "Quantity updated"}), 200


@app.route("/api/cart/<int:item_id>", methods=["DELETE"])
@login_required
def api_delete_cart_item(item_id):
    item = db.fetch_one(
        "SELECT * FROM cart_items WHERE id = %s AND user_id = %s", (item_id, current_user_id())
    )
    if not item:
        return jsonify({"error": "Cart item not found"}), 404

    db.execute("DELETE FROM cart_items WHERE id = %s", (item_id,))
    return jsonify({"message": "Item removed"}), 200


@app.route("/api/orders", methods=["POST"])
@login_required
def api_create_order():
    """Create an order directly from the cart via the REST API (JSON checkout)."""
    data = request.get_json(force=True)
    address = data.get("address", "").strip()
    if not address:
        return jsonify({"error": "Shipping address is required"}), 400

    items = db.fetch_all(
        """SELECT ci.quantity, p.id AS product_id, p.price, p.stock
           FROM cart_items ci JOIN products p ON p.id = ci.product_id
           WHERE ci.user_id = %s""",
        (current_user_id(),),
    )
    if not items:
        return jsonify({"error": "Cart is empty"}), 400

    total = sum(item["quantity"] * item["price"] for item in items)
    order_id, _ = db.execute(
        "INSERT INTO orders (user_id, total_amount, shipping_address) VALUES (%s, %s, %s)",
        (current_user_id(), total, address),
    )

    for item in items:
        db.execute(
            "INSERT INTO order_items (order_id, product_id, quantity, unit_price) VALUES (%s, %s, %s, %s)",
            (order_id, item["product_id"], item["quantity"], item["price"]),
        )
        db.execute("UPDATE products SET stock = stock - %s WHERE id = %s", (item["quantity"], item["product_id"]))

    db.execute("DELETE FROM cart_items WHERE user_id = %s", (current_user_id(),))
    return jsonify({"message": "Order placed", "order_id": order_id, "total": float(total)}), 201


@app.route("/api/orders", methods=["GET"])
@login_required
def api_list_orders():
    orders = db.fetch_all(
        "SELECT * FROM orders WHERE user_id = %s ORDER BY created_at DESC", (current_user_id(),)
    )
    return jsonify(orders), 200


if __name__ == "__main__":
    app.run(debug=True)
