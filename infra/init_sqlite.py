import os
import sqlite3
from pathlib import Path

base_dir = Path(__file__).resolve().parent
DB_PATH = base_dir / "mboahub.sqlite3"

if DB_PATH.exists():
    DB_PATH.unlink()

conn = sqlite3.connect(DB_PATH)
cur = conn.cursor()

cur.executescript(
    """
    CREATE TABLE users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        email TEXT NOT NULL UNIQUE,
        phone TEXT,
        password_hash TEXT NOT NULL,
        full_name TEXT NOT NULL,
        avatar_url TEXT,
        avatar_public_id TEXT,
        status TEXT NOT NULL DEFAULT 'pending_verification',
        email_verified_at TEXT,
        phone_verified_at TEXT,
        created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
        updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
    );

    CREATE TABLE user_roles (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
        role TEXT NOT NULL,
        created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
        UNIQUE (user_id, role)
    );

    CREATE TABLE shops (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        owner_id INTEGER NOT NULL UNIQUE REFERENCES users(id) ON DELETE CASCADE,
        name TEXT NOT NULL,
        slug TEXT NOT NULL UNIQUE,
        description TEXT,
        logo_url TEXT,
        logo_public_id TEXT,
        verification_status TEXT NOT NULL DEFAULT 'pending',
        created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
        updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
    );

    CREATE TABLE categories (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        slug TEXT NOT NULL UNIQUE,
        parent_id INTEGER REFERENCES categories(id) ON DELETE SET NULL,
        created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
    );

    CREATE TABLE products (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        shop_id INTEGER NOT NULL REFERENCES shops(id) ON DELETE CASCADE,
        category_id INTEGER REFERENCES categories(id) ON DELETE SET NULL,
        title TEXT NOT NULL,
        slug TEXT NOT NULL UNIQUE,
        description TEXT,
        price_cents INTEGER NOT NULL DEFAULT 0,
        currency TEXT NOT NULL DEFAULT 'USD',
        stock_quantity INTEGER NOT NULL DEFAULT 0,
        sku TEXT,
        status TEXT NOT NULL DEFAULT 'draft',
        created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
        updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
    );

    CREATE TABLE orders (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        customer_id INTEGER NOT NULL REFERENCES users(id) ON DELETE RESTRICT,
        shop_id INTEGER NOT NULL REFERENCES shops(id) ON DELETE RESTRICT,
        status TEXT NOT NULL DEFAULT 'PENDING_PAYMENT',
        subtotal_cents INTEGER NOT NULL DEFAULT 0,
        delivery_fee_cents INTEGER NOT NULL DEFAULT 0,
        total_cents INTEGER NOT NULL DEFAULT 0,
        currency TEXT NOT NULL DEFAULT 'USD',
        delivery_address_id INTEGER,
        created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
        updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
    );
    """
)

cur.execute("INSERT INTO users (email, password_hash, full_name, status) VALUES (?, ?, ?, ?)",
            ("admin@mboahub.local", "demo-hash", "Admin User", "active"))
conn.commit()

print(f"Database created at {DB_PATH}")
print("Tables:")
for row in cur.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name"):
    print(row[0])

cur.execute("SELECT id, email, full_name FROM users LIMIT 5")
print("Sample rows:")
for row in cur.fetchall():
    print(row)

conn.close()
