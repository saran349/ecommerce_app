-- ============================================================
-- E-Commerce Website — Database Schema (MySQL)
-- Run this once to create the database and seed sample products.
-- ============================================================

CREATE DATABASE IF NOT EXISTS ecommerce_db;
USE ecommerce_db;

-- ---------- USERS ----------
CREATE TABLE IF NOT EXISTS users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    full_name VARCHAR(120) NOT NULL,
    email VARCHAR(150) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ---------- PRODUCTS ----------
CREATE TABLE IF NOT EXISTS products (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(150) NOT NULL,
    description TEXT,
    price DECIMAL(10, 2) NOT NULL,
    category VARCHAR(80),
    stock INT NOT NULL DEFAULT 0,
    image_url VARCHAR(255),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ---------- CART ITEMS ----------
CREATE TABLE IF NOT EXISTS cart_items (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    product_id INT NOT NULL,
    quantity INT NOT NULL DEFAULT 1,
    added_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (product_id) REFERENCES products(id) ON DELETE CASCADE,
    UNIQUE KEY unique_user_product (user_id, product_id)
);

-- ---------- ORDERS ----------
CREATE TABLE IF NOT EXISTS orders (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    total_amount DECIMAL(10, 2) NOT NULL,
    status VARCHAR(30) NOT NULL DEFAULT 'placed',
    shipping_address VARCHAR(255),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

-- ---------- ORDER ITEMS ----------
CREATE TABLE IF NOT EXISTS order_items (
    id INT AUTO_INCREMENT PRIMARY KEY,
    order_id INT NOT NULL,
    product_id INT NOT NULL,
    quantity INT NOT NULL,
    unit_price DECIMAL(10, 2) NOT NULL,
    FOREIGN KEY (order_id) REFERENCES orders(id) ON DELETE CASCADE,
    FOREIGN KEY (product_id) REFERENCES products(id)
);

-- ---------- SEED DATA ----------
INSERT INTO products (name, description, price, category, stock, image_url) VALUES
('Wireless Mouse', 'Ergonomic 2.4GHz wireless mouse with USB receiver.', 599.00, 'Electronics', 50, 'https://picsum.photos/seed/mouse/300/200'),
('Mechanical Keyboard', 'RGB backlit mechanical keyboard, blue switches.', 2499.00, 'Electronics', 30, 'https://picsum.photos/seed/keyboard/300/200'),
('Cotton T-Shirt', 'Breathable 100% cotton round-neck t-shirt.', 399.00, 'Apparel', 100, 'https://picsum.photos/seed/tshirt/300/200'),
('Running Shoes', 'Lightweight running shoes with cushioned sole.', 1899.00, 'Footwear', 40, 'https://picsum.photos/seed/shoes/300/200'),
('Stainless Steel Bottle', 'Insulated 1L water bottle, keeps drinks cold 24h.', 699.00, 'Home & Kitchen', 60, 'https://picsum.photos/seed/bottle/300/200'),
('Bluetooth Headphones', 'Over-ear wireless headphones, 30h battery life.', 3299.00, 'Electronics', 25, 'https://picsum.photos/seed/headphones/300/200'),
('Yoga Mat', 'Non-slip 6mm thick yoga and exercise mat.', 899.00, 'Sports & Fitness', 45, 'https://picsum.photos/seed/yogamat/300/200'),
('Backpack', 'Water-resistant 25L backpack with laptop compartment.', 1599.00, 'Accessories', 35, 'https://picsum.photos/seed/backpack/300/200');
