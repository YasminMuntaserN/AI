import psycopg2


def create_tables(DB_CONFIG):
    """
    Create required tables if they do not already exist
    """

    try:
        with psycopg2.connect(**DB_CONFIG) as conn:

            with conn.cursor() as cur:

                # Products table
                cur.execute(
                    """
                    CREATE TABLE IF NOT EXISTS products (
                        id SERIAL PRIMARY KEY,
                        sku TEXT UNIQUE NOT NULL,
                        name TEXT NOT NULL,
                        aname TEXT NOT NULL,
                        price NUMERIC(10,2) NOT NULL CHECK (price >= 0),
                        stock INTEGER NOT NULL DEFAULT 0 CHECK (stock >= 0),
                        category TEXT,
                        description TEXT
                    );
                    """
                )

                cur.execute(
                    """
                    CREATE INDEX IF NOT EXISTS idx_products_category
                    ON products(category);
                    """
                )

                # Orders table
                cur.execute(
                    """
                    CREATE TABLE IF NOT EXISTS orders (
                        order_id TEXT PRIMARY KEY,
                        user_id TEXT NOT NULL,
                        sku TEXT NOT NULL,
                        total NUMERIC(12,2) NOT NULL CHECK (total >= 0),
                        status TEXT NOT NULL,
                        created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
                    );
                    """
                )

                # Order sequence
                cur.execute(
                    """
                    CREATE SEQUENCE IF NOT EXISTS order_seq START 1;
                    """
                )

            conn.commit()

        print("✅ Tables created successfully (if not existing).")

    except Exception as e:
        print(f"❌ Failed to create tables: {e}")


def seed_products(DB_CONFIG, products):
    """
    Insert initial product data
    """

    try:
        with psycopg2.connect(**DB_CONFIG) as conn:

            with conn.cursor() as cur:

                cur.executemany(
                    """
                    INSERT INTO products (sku, name, aname, price, stock, category, description)
                    VALUES (%s, %s, %s, %s, %s, %s, %s)
                    ON CONFLICT (sku) DO NOTHING
                    """,
                    products,
                )

            conn.commit()

        print("✅ Initial products inserted successfully.")

    except Exception as e:
        print(f"❌ Failed to insert products: {e}")
        raise