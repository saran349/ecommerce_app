# ShopEasy — E-Commerce Website

A full-stack e-commerce demo built to match the skills on the resume:
**Python, Flask, REST API, MySQL (mysql-connector), CRUD operations, HTML5, CSS3, JavaScript, Git-ready structure.**

## Features
- User registration & login (hashed passwords via Werkzeug)
- Product catalog with category filtering
- Product detail pages
- Cart: add / update quantity / remove — via a REST API, updated with JavaScript (no full page reload for add-to-cart)
- Checkout flow that creates an order, order items, and decrements stock
- Order history page
- A parallel REST API (`/api/...`) exposing the same CRUD operations as JSON, so this backend could power a mobile app or SPA frontend too

## Project Structure
```
ecommerce_app/
├── app.py                 # Flask app: page routes + REST API routes
├── db.py                  # MySQL connection + query helpers (mysql-connector)
├── schema.sql             # Database schema + seed products
├── requirements.txt
├── templates/              # Jinja2 HTML templates
│   ├── base.html
│   ├── index.html
│   ├── product.html
│   ├── cart.html
│   ├── checkout.html
│   ├── orders.html
│   ├── login.html
│   └── register.html
└── static/
    ├── css/style.css       # Responsive CSS3 styling
    └── js/main.js          # Fetch calls to the REST API
```

## Setup

### 1. Install MySQL and create the database
```bash
mysql -u root -p < schema.sql
```
This creates `ecommerce_db` with `users`, `products`, `cart_items`, `orders`, and `order_items` tables, plus 8 seed products.

### 2. Update database credentials
Edit `db.py` and set your MySQL username/password:
```python
DB_CONFIG = {
    "host": "localhost",
    "user": "root",
    "password": "yourpassword",
    "database": "ecommerce_db",
}
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. Run the app
```bash
python app.py
```
Visit **http://127.0.0.1:5000** in your browser.

## REST API Endpoints
| Method | Endpoint              | Description                          |
|--------|-----------------------|--------------------------------------|
| GET    | `/api/products`       | List all products                    |
| GET    | `/api/products/<id>`  | Get one product                      |
| GET    | `/api/cart`           | Get current user's cart (login req.) |
| POST   | `/api/cart`           | Add item to cart                     |
| PUT    | `/api/cart/<item_id>` | Update quantity                      |
| DELETE | `/api/cart/<item_id>` | Remove item from cart                |
| POST   | `/api/orders`         | Place an order from the cart (JSON)  |
| GET    | `/api/orders`         | List current user's orders           |

## Notes for interview prep
- CRUD is demonstrated end-to-end: Create (register, add to cart, place order), Read (product listing, cart, orders), Update (cart quantity), Delete (remove cart item).
- Passwords are never stored in plain text — `generate_password_hash` / `check_password_hash` from Werkzeug.
- SQL uses parameterized queries (`%s` placeholders) throughout to prevent SQL injection.
- The same cart logic exists twice on purpose: as server-rendered Flask routes (traditional web app) AND as a REST API (`/api/...`) called by `main.js` — a good example to explain the difference between server-side rendering and API-driven frontends, a question in your interview prep deck.
