"""
Telegram Client for MCP E-Commerce AI Agent

This client connects:
Telegram → MCP Server → Local LLM (Ollama)

Flow:
1. User sends message on Telegram
2. Message goes to MCP prompt (classification)
3. Local LLM decides which tool to call
4. MCP executes tool
5. Result is returned to user
"""

from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, filters

import asyncio
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

import json
import ollama
import re
import traceback


# ---------------------------------------------------------
# Get Telegram Token from MCP Server
# ---------------------------------------------------------
async def get_token_from_mcp() -> str:

    params = StdioServerParameters(
        command="python",
        args=["ecommerce_server.py"]
    )

    async with stdio_client(params) as (reader, writer):
        async with ClientSession(reader, writer) as session:
            await session.initialize()

            res = await session.read_resource("resource://telegram_token_resource")

            try:
                return res.contents[0].text.strip()
            except Exception:
                return ""


# ---------------------------------------------------------
# Extract JSON tool call from LLM response
# ---------------------------------------------------------
def extract_tool_args(raw_text):

    try:
        # Remove comments if any
        clean_text = re.sub(r'//.*', '', raw_text)

        # Extract JSON block
        match = re.search(r'\{.*\}', clean_text, re.DOTALL)

        if not match:
            return None, {}

        data = json.loads(match.group())

        return data.get("tool"), data.get("args", {})

    except Exception as e:
        print("JSON parsing error:", e)
        return None, {}


# ---------------------------------------------------------
# Main Logic: classify message → call tool
# ---------------------------------------------------------
async def classify_and_execute(user_id: str, message: str) -> str:

    try:
        server_params = StdioServerParameters(
            command="python",
            args=["ecommerce_server.py"]
        )

        async with stdio_client(server_params) as (reader, writer):
            async with ClientSession(reader, writer) as session:

                await session.initialize()

                # Get system prompt from MCP
                prompt = await session.get_prompt(
                    "ecommerce_prompt",
                    {"user_input": message}
                )

                prompt_text = prompt.messages[0].content.text

                # 🔥 IMPORTANT: Use YOUR LOCAL MODEL
                response = ollama.chat(
                    model="llama3.1-8b-local",
                    messages=[
                        {"role": "system", "content": prompt_text},
                        {"role": "user", "content": message}
                    ]
                )

                raw = response["message"]["content"].strip()

                print("LLM RAW OUTPUT:\n", raw)

                tool, args = extract_tool_args(raw)

                # If model fails → fallback response
                if not tool:
                    msg = await session.read_resource(
                        "resource://custom_data_snippet_resource"
                    )
                    return msg.contents[0].text

                args = args or {}
                args["user_id"] = str(user_id)

                result = await session.call_tool(tool, args)

                return (result.content[0].text or "").strip()

    except Exception as e:
        traceback.print_exc()
        return f"❌ Error:\n{str(e)}"


# ---------------------------------------------------------
# Handle Telegram Messages
# ---------------------------------------------------------
async def handle_message(update: Update, context):

    try:
        if not update.message or not update.message.text:
            return

        user_text = update.message.text.strip()
        user_id = str(update.effective_user.id)

        # ✅ Send immediate response (prevents timeout)
        await update.message.reply_text("⏳ Processing your request...")

        # Process in background
        reply = await classify_and_execute(user_id, user_text)

        # Send final result
        await update.message.reply_text(
            reply if reply else "No response from AI."
        )

    except Exception as e:
        import traceback
        traceback.print_exc()
        await update.message.reply_text("❌ Error occurred.")

# Main App Runner
def main():

    token = asyncio.run(get_token_from_mcp())

    if not token:
        raise RuntimeError("TELEGRAM_TOKEN not found")

    app = ApplicationBuilder().token(token).build()

    app.add_handler(
        MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message)
    )

    print("🤖 Bot is running... Press Ctrl+C to stop.")

    app.run_polling()


if __name__ == "__main__":
    main()