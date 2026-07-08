"""
db.py — MySQL connection helper built on mysql-connector-python.

Centralizes all raw SQL CRUD access so routes stay clean.
"""
import mysql.connector
from mysql.connector import Error


DB_CONFIG = {
    "host": "localhost",
    "user": "root",          # change to your MySQL username
    "password": "",  # change to your MySQL password
    "database": "ecommerce_db",
}


def get_connection():
    """Open a new MySQL connection using mysql-connector."""
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        return conn
    except Error as e:
        print(f"[DB ERROR] Could not connect to MySQL: {e}")
        raise


def fetch_all(query, params=None):
    """Run a SELECT query and return a list of dict rows."""
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute(query, params or ())
    rows = cursor.fetchall()
    cursor.close()
    conn.close()
    return rows


def fetch_one(query, params=None):
    """Run a SELECT query and return a single dict row (or None)."""
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute(query, params or ())
    row = cursor.fetchone()
    cursor.close()
    conn.close()
    return row


def execute(query, params=None):
    """Run an INSERT / UPDATE / DELETE query. Returns (lastrowid, rowcount)."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(query, params or ())
    conn.commit()
    last_id, row_count = cursor.lastrowid, cursor.rowcount
    cursor.close()
    conn.close()
    return last_id, row_count
