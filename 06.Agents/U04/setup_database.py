import os
from dotenv import load_dotenv

import db_functions as db

load_dotenv()

DB_CONFIG = {
    "user": os.getenv("DB_USER"),
    "password": os.getenv("DB_PASSWORD"),
    "host": os.getenv("DB_HOST"),
    "port": int(os.getenv("DB_PORT", 5432)),
    "dbname": os.getenv("DB_NAME"),
    "sslmode": "require"   # required for Supabase
}


products_list = [

("IPH-15-BLU", "iPhone 15 - Blue", "iPhone 15 Blue", 3999, 80, "Mobile", "Latest generation iPhone with A16 chip"),
("IPH-15-PNK", "iPhone 15 - Pink", "iPhone 15 Pink", 3999, 70, "Mobile", "Elegant design with improved camera system"),
("IPH-15-PRM", "iPhone 15 Pro Max - Titanium", "iPhone 15 Pro Max Titanium", 5299, 50, "Mobile", "Flagship iPhone with top performance and lightweight titanium body"),
("IPH-14-RED", "iPhone 14 - Red", "iPhone 14 Red", 3399, 60, "Mobile", "Powerful smartphone with longer battery life and Super Retina display"),
("IPH-14-GRN", "iPhone 14 - Green", "iPhone 14 Green", 3399, 65, "Mobile", "Great performance with stylish color options"),

("SAM-S24-BLK", "Samsung Galaxy S24 - Black", "Samsung Galaxy S24 Black", 3799, 90, "Mobile", "Premium flagship phone with powerful processor and advanced camera"),
("SAM-S24-WHT", "Samsung Galaxy S24 - White", "Samsung Galaxy S24 White", 3799, 85, "Mobile", "High performance smartphone with stunning display"),

("SAM-A55-BLU", "Samsung Galaxy A55 - Blue", "Samsung Galaxy A55 Blue", 1799, 150, "Mobile", "Mid-range smartphone with strong battery and solid performance"),
("SAM-A55-GRN", "Samsung Galaxy A55 - Green", "Samsung Galaxy A55 Green", 1799, 140, "Mobile", "Great display and reliable camera system")

]

if __name__ == "__main__":

    db.create_tables(DB_CONFIG)

    db.seed_products(DB_CONFIG, products_list)