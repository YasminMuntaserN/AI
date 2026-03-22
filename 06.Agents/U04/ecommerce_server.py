"""
MCP E-Commerce AI Agent Server

This file implements an MCP server that allows an AI agent to interact
with an e-commerce database. The agent can perform several operations:

1. Search for products
2. Place an order
3. Track an order
4. Cancel an order
5. List all orders for a user

The server exposes these capabilities as MCP tools.
"""

# MCP framework used to expose tools/resources/prompts to an AI model
from mcp.server.fastmcp import FastMCP

# PostgreSQL connector used to communicate with the database
import psycopg2

# Local module that contains helper database functions
import db_functions as db

# Standard libraries
import os
import sys
from datetime import datetime

# Library used to load environment variables from a .env file
from dotenv import load_dotenv


# Encoding Fix
# This ensures that Python prints Unicode characters correctly.
# Without this, Arabic or other UTF-8 text may appear corrupted.
sys.stdout.reconfigure(encoding="utf-8")


# ---------------------------------------------------------

# Load Environment Variables
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
ENV_PATH = BASE_DIR / ".env"

load_dotenv(ENV_PATH)

print("ENV PATH =", ENV_PATH)
print("TELEGRAM_TOKEN =", os.getenv("TELEGRAM_TOKEN"))

# Initialize MCP Server
# The name "mcp-ecommerce" identifies this MCP server instance
mcp = FastMCP("mcp-ecommerce")


# MCP RESOURCES
# Resources provide data/configuration to the AI agent.


# PostgreSQL Base Configuration
# Returns connection settings for PostgreSQL.
# These values are loaded from the .env file.
@mcp.resource("resource://pg_config_resource")
def pg_config_resource():
    return {
        "user": os.getenv("DB_USER"),
        "password": os.getenv("DB_PASSWORD"),
        "host": os.getenv("DB_HOST"),
        "port": int(os.getenv("DB_PORT", 5432)),
        "sslmode": "require"  # required for Supabase connections
    }


# Database Name Resource
# Returns the name of the PostgreSQL database.
@mcp.resource("resource://db_name_resource")
def db_name_resource():
    return os.getenv("DB_NAME")


# Full Database Configuration
# Combines base PostgreSQL config with the database name.
@mcp.resource("resource://db_config_resource")
def db_config_resource():
    DB_CONFIG = pg_config_resource().copy()
    DB_CONFIG["dbname"] = os.getenv("DB_NAME")
    return DB_CONFIG


# Custom Store Information Resource
# Reads a file that contains additional store information
# such as policies, contact info, shipping info, etc.
@mcp.resource("resource://custom_data_snippet_resource")
def custom_data_snippet_resource():
    with open("ecommerce_data.txt", encoding="utf-8") as f:
        return f.read()


# Telegram Token Resource
# This allows integration with Telegram if the bot is used there.
@mcp.resource("resource://telegram_token_resource")
def telegram_token_resource():
    token = os.getenv("TELEGRAM_TOKEN", "")
    return f"{token}"


# HELPER FUNCTIONS

# Database Connection Helper
# This function opens a connection to PostgreSQL using psycopg2.
# It reuses the configuration from db_config_resource().
def _connect():
    DB_CONFIG = db_config_resource()
    return psycopg2.connect(**DB_CONFIG)


# MCP TOOLS


# Tool 1: Search Products
@mcp.tool(name="search_products")
def search_products(q="", limit=10):
    """
    Smart product search with keyword normalization and fallback handling
    """
    try:
        with _connect() as cn, cn.cursor() as cur:

            if q:
                q_clean = q.lower().strip()

                # 🔹 Normalize keywords
                stopwords = ["mobiles", "mobile", "phones", "phone"]
                for word in stopwords:
                    q_clean = q_clean.replace(word, "").strip()

                synonyms = {
                    "iphones": "iphone",
                    "iphone": "iphone",
                    "apple": "iphone",
                    "samsung": "samsung",
                    "galaxy": "samsung"
                }

                for key in synonyms:
                    if key in q_clean:
                        q_clean = synonyms[key]
                        break

                sql = """
                SELECT id, sku, name, price, stock, category, description
                FROM products
                WHERE
                    LOWER(name) LIKE %s OR
                    LOWER(sku) LIKE %s OR
                    LOWER(category) LIKE %s OR
                    LOWER(description) LIKE %s
                ORDER BY name
                LIMIT %s
                """
                like = f"%{q_clean}%"
                cur.execute(sql, (like, like, like, like, limit))
                rows = cur.fetchall()

                if not rows:
                    return f"No products found matching '{q}'. Try keywords like 'iPhone' or 'Samsung'."

            else:
                # Default top products
                cur.execute("""
                    SELECT id, sku, name, price, stock, category, description
                    FROM products
                    ORDER BY stock DESC
                    LIMIT %s
                """, (limit,))
                rows = cur.fetchall()

            result = "📦 Available products:\n\n"
            for r in rows:
                result += (
                    f"📱 {r[2]}\n"
                    f"SKU: {r[1]}\n"
                    f"💰 Price: {r[3]}\n"
                    f"📦 Stock: {r[4]}\n"
                    f"📂 Category: {r[5]}\n"
                    f"📝 {r[6]}\n\n"
                )
            result += "👉 To order, send the SKU."
            return result

    except Exception as e:
        return f"Database error: {e}"

        
# Tool 2: Add Order
@mcp.tool(name="add_order")
def add_order(sku="", user_id="GUEST"):

    if not sku:
        return "You must provide a product SKU."

    try:
        with _connect() as cn, cn.cursor() as cur:

            # Check if product exists
            cur.execute(
                """
                SELECT name, price, stock, category, description
                FROM products
                WHERE sku=%s
                """,
                (sku,)
            )

            row = cur.fetchone()

            if not row:
                return "Product not found."

            name, price, stock, category, description = row

            if stock <= 0:
                return "Product is out of stock."

            # Generate order ID
            cur.execute("SELECT nextval('order_seq')")
            seq = cur.fetchone()[0]

            year = datetime.now().year
            order_id = f"ORD-{year}-{seq:05d}"

            # Insert order
            cur.execute(
                """
                INSERT INTO orders (order_id, user_id, sku, total, status)
                VALUES (%s,%s,%s,%s,%s)
                """,
                (order_id, user_id, sku, price, "created")
            )

            # Decrease stock
            cur.execute(
                "UPDATE products SET stock = stock - 1 WHERE sku=%s",
                (sku,)
            )

            cn.commit()

        return (
            f"Order created successfully\n\n"
            f"Order ID: {order_id}\n"
            f"Product: {name}\n"
            f"Price: {price}\n"
            f"Status: created"
        )

    except Exception as e:
        return f"Database error: {e}"


# Tool 3: Track Order
@mcp.tool(name="track_order")
def track_order(order_id: str):

    if not order_id:
        return "Please provide an order ID."

    try:
        with _connect() as cn, cn.cursor() as cur:

            cur.execute(
                "SELECT status FROM orders WHERE order_id=%s",
                (order_id,)
            )

            row = cur.fetchone()

            if not row:
                return "Order not found."

            status = row[0]

        return f"Order {order_id} status: {status}"

    except Exception as e:
        return f"Database error: {e}"


# Tool 4: Cancel Order
@mcp.tool(name="cancel_order")
def cancel_order(order_id):

    if not order_id:
        return "Order ID required."

    try:
        with _connect() as cn, cn.cursor() as cur:

            cur.execute(
                "SELECT status, sku FROM orders WHERE order_id=%s",
                (order_id,)
            )

            row = cur.fetchone()

            if not row:
                return "Order not found."

            status, sku = row

            if status in ("cancelled", "shipped", "delivered"):
                return f"Order cannot be cancelled. Current status: {status}"

            # Cancel order
            cur.execute(
                "UPDATE orders SET status='cancelled' WHERE order_id=%s",
                (order_id,)
            )

            # Restore stock
            cur.execute(
                "UPDATE products SET stock=stock+1 WHERE sku=%s",
                (sku,)
            )

            cn.commit()

        return f"Order {order_id} cancelled successfully."

    except Exception as e:
        return f"Database error: {e}"


# Tool 5: List User Orders
@mcp.tool(name="list_user_orders")
def list_user_orders(user_id="GUEST"):

    try:
        with _connect() as cn, cn.cursor() as cur:

            cur.execute(
                """
                SELECT
                    o.order_id,
                    o.status,
                    o.total,
                    p.name,
                    p.category
                FROM orders o
                LEFT JOIN products p
                ON p.sku=o.sku
                WHERE o.user_id=%s
                ORDER BY o.order_id DESC
                """,
                (user_id,)
            )

            rows = cur.fetchall()

        if not rows:
            return "No orders found."

        result = ""

        for r in rows:
            result += (
                f"Order ID: {r[0]}\n"
                f"Status: {r[1]}\n"
                f"Product: {r[3]}\n"
                f"Category: {r[4]}\n"
                f"Total: {r[2]}\n\n"
            )

        return result

    except Exception as e:
        return f"Database error: {e}"


# Default Tool
# Used when user request is unclear
@mcp.tool(name="default_response")
def default_response():
    return "I can help you search products, place orders, track orders, or cancel orders."


# MCP PROMPT (Agent Decision System)
@mcp.prompt(
    name="ecommerce_prompt",
    description="Smart tool selection and argument extraction"
)
def ecommerce_prompt(user_input: str):

    return f"""
You are a highly intelligent AI assistant for an e-commerce platform.

Your job is to:
1. Understand the user's intent
2. Choose the correct tool
3. Extract the correct arguments

⚠️ CRITICAL RULES:
- You MUST return ONLY a valid JSON object
- DO NOT write explanations
- DO NOT write text outside JSON
- DO NOT include comments

-------------------------------------

OUTPUT FORMAT:

{{
  "tool": "tool_name",
  "args": {{}}
}}

-------------------------------------

AVAILABLE TOOLS:

- search_products → when user asks about products
- add_order → when user wants to buy something
- track_order → when user asks about order status
- cancel_order → when user wants to cancel an order
- list_user_orders → when user asks about their orders
- default_response → for anything else

-------------------------------------

ARGUMENT RULES:

1. search_products:
   - ALWAYS extract a keyword into "q"
   - Examples:
     "iPhone", "Samsung", "laptop", "blue phone"

2. add_order:
   - MUST include "sku"
   - Extract exact SKU from user message

3. track_order:
   - MUST include "order_id"

4. cancel_order:
   - MUST include "order_id"

5. list_user_orders:
   - No extra args needed

-------------------------------------

EXAMPLES:

User: Do you have iPhone?
Response:
{{"tool": "search_products", "args": {{"q": "iphone"}}}}

User: I want to buy SAM-A55-BLU
Response:
{{"tool": "add_order", "args": {{"sku": "SAM-A55-BLU"}}}}

User: track order ORD-2026-00001
Response:
{{"tool": "track_order", "args": {{"order_id": "ORD-2026-00001"}}}}

User: cancel order ORD-2026-00001
Response:
{{"tool": "cancel_order", "args": {{"order_id": "ORD-2026-00001"}}}}

User: what are my orders?
Response:
{{"tool": "list_user_orders", "args": {{}}}}

-------------------------------------

USER MESSAGE:
{user_input}
"""

# SERVER START
if __name__ == "__main__":

    try:

        DB_CONFIG = db_config_resource()

        # Create tables if not existing
        db.create_tables(DB_CONFIG)

        # Start MCP server
        mcp.run(transport="stdio")

    except KeyboardInterrupt:
        print("Server stopped.")

    except Exception as e:
        print(f"Error: {e}")