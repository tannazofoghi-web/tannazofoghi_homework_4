# Online Shop — ShopEase

## 1. Project title
**Online Shop (ShopEase)**

## 2. Project overview
ShopEase is a small educational online shop built with Python, Flask, SQLite (SQL), HTML, CSS, and JavaScript. Customers can browse products, add products to a cart, log in, and place a demo order. An administrator can sign in, add or delete products, and review orders.

## 3. Main pages and features
- **Home page:** shows available products and prices.
- **Secure Login:** checks a username and password hash.
- **Admin Home Page:** lets an administrator manage products and review orders.
- **Shopping Cart:** lists selected products and calculates the total.
- **Checkout:** saves an order and its items to the database.
- **Responsive frontend:** adapts to phone, tablet, and desktop screens.

## 4. Technical stack
- **Programming language:** Python
- **Backend framework:** Flask
- **Database:** SQLite, a SQL relational database
- **Frontend:** HTML, CSS, JavaScript
- **Database connection:** Python's built-in `sqlite3` module
- **Password security:** Werkzeug password hashing

## 5. Database
When `app.py` starts, `init_db()` creates four related tables:
- `users`: login name, password hash, and role
- `products`: product details, price, and stock
- `orders`: customer, order time, total, and status
- `order_items`: products and quantities belonging to each order

Primary keys identify rows. Foreign keys connect order items to orders and products. SQL parameters (`?`) are used in queries to reduce SQL-injection risk.

## 6. Run locally
1. Install Python 3.10 or newer.
2. Open a terminal in the project folder.
3. Create a virtual environment:
   - Windows: `py -m venv .venv`
   - macOS/Linux: `python3 -m venv .venv`
4. Activate it:
   - Windows PowerShell: `.venv\\Scripts\\Activate.ps1`
   - macOS/Linux: `source .venv/bin/activate`
5. Install dependencies: `pip install -r requirements.txt`
6. Start the app: `python app.py`
7. Open `http://127.0.0.1:5000` in your browser.

The database file `shop.db` and sample products are created automatically the first time the application runs.

## 7. Demo administrator account
- Username: `admin`
- Password: `ChangeMe123!`

This is a demo account for local classroom testing only. Change the password and set a strong `SECRET_KEY` environment variable before any public deployment. Do not publish a real password or secret.

## 8. Upload to GitHub
Create a new repository on GitHub. Upload the project files and folders, keeping the folder structure shown below. Do not upload `.venv`, `.env`, or `shop.db`. GitHub stores the source code; it does not automatically run the Flask website.

## 9. Project structure
```text
online_shop_project/
├── app.py
├── requirements.txt
├── README.md
├── .gitignore
├── templates/
│   ├── base.html
│   ├── index.html
│   ├── login.html
│   ├── admin_home.html
│   ├── cart.html
│   └── error.html
├── static/
│   ├── css/style.css
│   └── js/main.js
└── tests/
```

## 10. Important limitations
This is a classroom/demo project, not a production-ready store. It does not process real payments, send emails, or include customer registration. Before real deployment, add CSRF protection, secure session-cookie settings, a production WSGI server, stronger configuration, and a complete security review.
