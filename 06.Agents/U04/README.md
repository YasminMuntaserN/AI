# 🤖 AI E-Commerce Agent with MCP + Ollama + Telegram

## 📌 Project Overview

This project is an intelligent AI-powered e-commerce assistant that allows users to:

- 🔍 Search for products
- 🛒 Place orders
- 📦 Track orders
- ❌ Cancel orders
- 📋 View all their orders

The system uses a **local LLM (Llama 3.1 via Ollama)** combined with an **MCP (Model Context Protocol) server** and integrates with **Telegram** for real-time interaction.

---

## 🏗️ Architecture

```
User (Telegram / Desktop)
        ↓
Telegram Bot Client
        ↓
MCP Client (Python)
        ↓
MCP Server (FastMCP)
        ↓
Tools (Search / Orders)
        ↓
PostgreSQL (Supabase)
        ↓
Response → User
```

---

## 🧠 Technologies Used

- Python
- Ollama (Local LLM - Llama 3.1)
- MCP (Model Context Protocol)
- PostgreSQL (Supabase)
- python-telegram-bot
- psycopg2
- dotenv

---

## ⚙️ Setup Instructions

### 1. Clone the Repository

```bash
git clone <your-repo-url>
cd project-folder
```

---

### 2. Install Dependencies

```bash
uv add ollama
uv add python-telegram-bot
uv add psycopg2-binary
uv add python-dotenv
```

---

### 3. Setup Environment Variables (.env)

Create a `.env` file:

```env
DB_USER=your_user
DB_PASSWORD=your_password
DB_HOST=your_host
DB_PORT=5432
DB_NAME=your_db

TELEGRAM_TOKEN=your_bot_token
```

---

### 4. Setup Database

Run:

```bash
python setup_database.py
```

This will:
- Create tables
- Insert sample products

---

### 5. Setup Ollama Model

Download model:

```bash
ollama create llama3.1-8b-local -f Modelfile
```

Run test:

```bash
ollama run llama3.1-8b-local
```

---

### 6. Run MCP Server

```bash
python ecommerce_server.py
```

---

### 7. Run Telegram Bot

```bash
uv run .\ecommerce_Telegram_client.py
```

---

### 8. Create Telegram Bot

1. Open Telegram
2. Search for **BotFather**
3. Send:
   ```
   /newbot
   ```
4. Choose a name (must end with `bot`)
5. Copy the token into `.env`

---

## 🧪 Example Use Cases

### Search Products
![Search Products](assets/c_Search%20products.png)
![Bot Greeting](assets/Search%20products.png)


### Add Order
![Add Order](assets/c_add%20order.png)
![Add Order](assets/add%20order.png)


### Cancel Order
![Cancel Order](assets/cancle%20order.png)
![Cancel Order](assets/c_cancle%20order.png)


### Track Order
![Track Order](assets/c_track%20order.png)

### List User Orders
![List Orders](assets/list%20orders.png)
![List Orders](assets/c_list%20orders.png)


---

## 📂 Project Structure

```
project/
│
├── ecommerce_server.py
├── ecommerce_Telegram_client.py
├── db_functions.py
├── seed_script.py
├── ecommerce_data.txt
├── Modelfile
├── .env
└── README.md
```

---

## 🚀 Features

- Local AI (No OpenAI API required)
- Tool-based architecture (MCP)
- Real-time Telegram interaction
- PostgreSQL integration
- Smart product search

---

## ⚠️ Notes

- Local model may be less accurate than GPT-4
- Ensure Ollama is running before starting the bot
- Use correct model name: `llama3.1-8b-local`

---
