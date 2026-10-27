from functools import wraps
import os
import sqlite3
from flask import Flask, render_template, request, redirect, url_for, session, flash, abort
from werkzeug.security import generate_password_hash, check_password_hash

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DATABASE = os.path.join(BASE_DIR, "shop.db")

app = Flask(__name__)
# For real deployment, set SECRET_KEY as an environment variable.
app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY", "dev-only-change-this-secret-key")


def get_db():
    """Open a SQLite connection and return rows as dictionary-like objects."""
    connection = sqlite3.connect(DATABASE)
    connection.row_factory = sqlite3.Row
    connection.execute("PRAGMA foreign_keys = ON")
    return connection


def init_db():
    """Create tables and insert sample products/admin if the database is new."""
    with get_db() as db:
        db.executescript("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT NOT NULL UNIQUE,
                password_hash TEXT NOT NULL,
                role TEXT NOT NULL DEFAULT 'customer'
            );

            CREATE TABLE IF NOT EXISTS products (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                description TEXT NOT NULL DEFAULT '',
                price REAL NOT NULL CHECK(price >= 0),
                stock INTEGER NOT NULL DEFAULT 0 CHECK(stock >= 0),
                image_url TEXT NOT NULL DEFAULT ''
            );

            CREATE TABLE IF NOT EXISTS orders (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT NOT NULL,
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                total REAL NOT NULL,
                status TEXT NOT NULL DEFAULT 'Received'
            );

            CREATE TABLE IF NOT EXISTS order_items (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                order_id INTEGER NOT NULL,
                product_id INTEGER NOT NULL,
                quantity INTEGER NOT NULL CHECK(quantity > 0),
                unit_price REAL NOT NULL,
                FOREIGN KEY(order_id) REFERENCES orders(id),
                FOREIGN KEY(product_id) REFERENCES products(id)
            );
        """)

        admin = db.execute("SELECT id FROM users WHERE username = ?", ("admin",)).fetchone()
        if admin is None:
            db.execute(
                "INSERT INTO users (username, password_hash, role) VALUES (?, ?, ?)",
                ("admin", generate_password_hash("ChangeMe123!"), "admin")
            )

        product_count = db.execute("SELECT COUNT(*) AS count FROM products").fetchone()["count"]
        if product_count == 0:
            sample_products = [
                ("Wireless Headphones", "Comfortable headphones for everyday listening.", 39.99, 12, ""),
                ("Desk Lamp", "A simple adjustable lamp for your workspace.", 24.50, 8, ""),
                ("Reusable Bottle", "A reusable bottle for school, work, or travel.", 12.00, 20, ""),
            ]
            db.executemany(
                "INSERT INTO products (name, description, price, stock, image_url) VALUES (?, ?, ?, ?, ?)",
                sample_products
            )


def login_required(view):
    @wraps(view)
    def wrapped(*args, **kwargs):
        if "username" not in session:
            flash("Please log in to continue.", "warning")
            return redirect(url_for("login"))
        return view(*args, **kwargs)
    return wrapped


def admin_required(view):
    @wraps(view)
    def wrapped(*args, **kwargs):
        if "username" not in session:
            flash("Please log in first.", "warning")
            return redirect(url_for("login"))
        if session.get("role") != "admin":
            abort(403)
        return view(*args, **kwargs)
    return wrapped


@app.route("/")
def home():
    with get_db() as db:
        products = db.execute("SELECT * FROM products ORDER BY id DESC").fetchall()
    return render_template("index.html", products=products)


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")
        with get_db() as db:
            user = db.execute(
                "SELECT * FROM users WHERE username = ?", (username,)
            ).fetchone()

        if user and check_password_hash(user["password_hash"], password):
            session.clear()
            session["username"] = user["username"]
            session["role"] = user["role"]
            flash("You are now logged in.", "success")
            return redirect(url_for("admin_home") if user["role"] == "admin" else url_for("home"))

        flash("Incorrect username or password.", "error")
    return render_template("login.html")


@app.route("/logout")
def logout():
    session.clear()
    flash("You have been logged out.", "success")
    return redirect(url_for("home"))


@app.route("/admin")
@admin_required
def admin_home():
    with get_db() as db:
        products = db.execute("SELECT * FROM products ORDER BY id DESC").fetchall()
        orders = db.execute("SELECT * FROM orders ORDER BY id DESC").fetchall()
    return render_template("admin_home.html", products=products, orders=orders)


@app.route("/admin/products/add", methods=["POST"])
@admin_required
def add_product():
    name = request.form.get("name", "").strip()
    description = request.form.get("description", "").strip()
    image_url = request.form.get("image_url", "").strip()
    try:
        price = float(request.form.get("price", ""))
        stock = int(request.form.get("stock", ""))
        if not name or price < 0 or stock < 0:
            raise ValueError
    except ValueError:
        flash("Enter a name, a non-negative price, and a non-negative stock quantity.", "error")
        return redirect(url_for("admin_home"))

    with get_db() as db:
        db.execute(
            "INSERT INTO products (name, description, price, stock, image_url) VALUES (?, ?, ?, ?, ?)",
            (name, description, price, stock, image_url)
        )
    flash("Product added.", "success")
    return redirect(url_for("admin_home"))


@app.route("/admin/products/delete/<int:product_id>", methods=["POST"])
@admin_required
def delete_product(product_id):
    with get_db() as db:
        product = db.execute("SELECT id FROM products WHERE id = ?", (product_id,)).fetchone()
        if product is None:
            abort(404)
        linked = db.execute("SELECT id FROM order_items WHERE product_id = ?", (product_id,)).fetchone()
        if linked:
            flash("This product is part of an order and cannot be deleted.", "warning")
        else:
            db.execute("DELETE FROM products WHERE id = ?", (product_id,))
            flash("Product deleted.", "success")
    return redirect(url_for("admin_home"))


@app.route("/cart/add/<int:product_id>", methods=["POST"])
def add_to_cart(product_id):
    with get_db() as db:
        product = db.execute("SELECT * FROM products WHERE id = ?", (product_id,)).fetchone()
    if product is None:
        abort(404)
    if product["stock"] < 1:
        flash("This product is out of stock.", "warning")
        return redirect(url_for("home"))

    cart = session.get("cart", {})
    key = str(product_id)
    current_qty = int(cart.get(key, 0))
    if current_qty >= product["stock"]:
        flash("There is not enough stock for another item.", "warning")
    else:
        cart[key] = current_qty + 1
        session["cart"] = cart
        flash("Added to cart.", "success")
    return redirect(url_for("home"))


@app.route("/cart")
def view_cart():
    cart = session.get("cart", {})
    items = []
    total = 0.0
    with get_db() as db:
        for product_id, quantity in cart.items():
            product = db.execute("SELECT * FROM products WHERE id = ?", (product_id,)).fetchone()
            if product:
                line_total = product["price"] * int(quantity)
                items.append({"product": product, "quantity": int(quantity), "line_total": line_total})
                total += line_total
    return render_template("cart.html", items=items, total=total)


@app.route("/checkout", methods=["POST"])
@login_required
def checkout():
    cart = session.get("cart", {})
    if not cart:
        flash("Your cart is empty.", "warning")
        return redirect(url_for("view_cart"))

    with get_db() as db:
        validated = []
        total = 0.0
        for product_id, quantity in cart.items():
            product = db.execute("SELECT * FROM products WHERE id = ?", (product_id,)).fetchone()
            quantity = int(quantity)
            if product is None or quantity < 1 or quantity > product["stock"]:
                flash("A product is no longer available in the requested quantity.", "error")
                return redirect(url_for("view_cart"))
            validated.append((product, quantity))
            total += product["price"] * quantity

        cursor = db.execute(
            "INSERT INTO orders (username, total) VALUES (?, ?)",
            (session["username"], round(total, 2))
        )
        order_id = cursor.lastrowid
        for product, quantity in validated:
            db.execute(
                "INSERT INTO order_items (order_id, product_id, quantity, unit_price) VALUES (?, ?, ?, ?)",
                (order_id, product["id"], quantity, product["price"])
            )
            db.execute(
                "UPDATE products SET stock = stock - ? WHERE id = ?",
                (quantity, product["id"])
            )

    session["cart"] = {}
    flash(f"Order #{order_id} received successfully.", "success")
    return redirect(url_for("home"))


@app.errorhandler(403)
def forbidden(_error):
    return render_template("error.html", message="You do not have permission to view this page."), 403


@app.errorhandler(404)
def not_found(_error):
    return render_template("error.html", message="The requested page or item was not found."), 404


init_db()

if __name__ == "__main__":
    # Debug mode is useful for local learning only; do not enable it in production.
    app.run(debug=True)
