"""
Main test file for database functions.

This file:
1. Loads database configuration from .env
2. Connects to Supabase PostgreSQL
3. Creates tables if they don't exist
4. Tests customer functions
"""

import db_functions as db
import os
from dotenv import load_dotenv

# Load environment variables from .env
load_dotenv()

# Database configuration dictionary
DB_CONFIG = {
    "user": os.getenv("DB_USER"),          # Database username
    "password": os.getenv("DB_PASSWORD"),  # Database password
    "host": os.getenv("DB_HOST"),          # Supabase database host
    "port": int(os.getenv("DB_PORT", 5432)),
    "dbname": os.getenv("DB_NAME"),        # Database name
    "sslmode": "require"                   # Required for Supabase
}


if __name__ == "__main__":

    # Create tables if they do not exist
    db.create_tables(DB_CONFIG)

    # Test customer data
    mobile = "123456789"
    email = "test@test.com"

    # Insert or update customer
    db.add_or_update_customer(mobile, email, DB_CONFIG)

    # Get email
    email = db.get_email(mobile, DB_CONFIG)
    print("email =", email)

    # Check if email missing
    missing_email = db.check_missing_email(mobile, DB_CONFIG)
    print("missing_email =", missing_email)