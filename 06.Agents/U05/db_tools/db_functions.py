"""
Database utility functions for the AI agent project.

Handles:
- Table creation
- Customer management
- Conversation logging
"""

import psycopg2


def create_tables(DB_CONFIG):
    """
    Creates required tables if they do not exist.
    """

    try:
        with psycopg2.connect(**DB_CONFIG) as conn:

            with conn.cursor() as cur:

                # Customers table
                cur.execute("""
                    CREATE TABLE IF NOT EXISTS customers (
                        mobile TEXT PRIMARY KEY,
                        email TEXT,
                        created_at TIMESTAMP DEFAULT NOW()
                    );
                """)

                # Conversations table (used for AI memory)
                cur.execute("""
                    CREATE TABLE IF NOT EXISTS conversations (
                        id SERIAL PRIMARY KEY,
                        mobile TEXT,
                        role TEXT,
                        content TEXT,
                        timestamp TIMESTAMP DEFAULT NOW()
                    );
                """)

            conn.commit()

        print("✅ Tables created successfully.")

    except Exception as e:
        print(f"❌ Failed to create tables: {e}")


def add_or_update_customer(mobile, email="", DB_CONFIG=None):
    """
    Inserts a new customer or updates email if customer already exists.
    """

    try:

        with psycopg2.connect(**DB_CONFIG) as conn:

            with conn.cursor() as cur:

                # Check if customer exists
                cur.execute(
                    "SELECT 1 FROM customers WHERE mobile = %s",
                    (mobile,)
                )

                exists = cur.fetchone() is not None

                if not exists:

                    # Insert new customer
                    cur.execute(
                        "INSERT INTO customers (mobile, email) VALUES (%s, %s)",
                        (mobile, email)
                    )

                else:

                    # Update email if provided
                    if email and email.strip():

                        cur.execute(
                            "UPDATE customers SET email = %s WHERE mobile = %s",
                            (email, mobile)
                        )

    except Exception as e:
        print(f"❌ Failed to insert/update customer: {e}")


def log_conversation(mobile: str, role: str, content: str, DB_CONFIG):
    """
    Saves conversation messages for AI memory.
    """

    try:
        with psycopg2.connect(**DB_CONFIG) as conn:

            with conn.cursor() as cur:

                cur.execute("""
                    INSERT INTO conversations (mobile, role, content)
                    VALUES (%s, %s, %s)
                """, (mobile, role, content))

    except Exception as e:
        print(f"❌ Failed to log conversation: {e}")


def get_email(mobile: str, DB_CONFIG):
    """
    Retrieves email address for a customer.
    """

    try:

        with psycopg2.connect(**DB_CONFIG) as conn:

            with conn.cursor() as cur:

                cur.execute(
                    "SELECT email FROM customers WHERE mobile = %s",
                    (mobile,)
                )

                row = cur.fetchone()

                if row and row[0]:
                    return row[0]

                return None

    except Exception as e:
        print(f"❌ Failed to retrieve email: {e}")
        return None


def check_missing_email(mobile: str, DB_CONFIG):
    """
    Checks if the customer email is missing.
    """

    try:

        with psycopg2.connect(**DB_CONFIG) as conn:

            with conn.cursor() as cur:

                cur.execute(
                    "SELECT email FROM customers WHERE mobile = %s",
                    (mobile,)
                )

                result = cur.fetchone()

                # True if email missing
                return result is None or not result[0] or result[0].strip() == ""

    except Exception as e:
        print(f"❌ Failed to check email: {e}")
        return True