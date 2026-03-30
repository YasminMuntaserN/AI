# Import Telegram bot core classes
from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, filters

# Async support
import asyncio

# MCP client (to communicate with your AI server)
from mcp import ClientSession
from mcp import StdioServerParameters  # Defines how to run the MCP server
from mcp.client.stdio import stdio_client

# Utilities
import json
import ollama   # Local LLM (llama3.1-8b-local)
import re


# FUNCTION: Get Telegram Bot Token from MCP Server
# This function starts the MCP server and reads the Telegram token
# from a resource defined inside the server.
async def get_token_from_mcp() -> str:

    params = StdioServerParameters(
        command="uv",
        args=["run", "appointment_server.py"]
    )

    async with stdio_client(params) as (reader, writer):
        async with ClientSession(reader, writer) as session:

            await session.initialize()

            # Read token from MCP resource
            res = await session.read_resource("resource://telegram_token_resource")

            try:
                return res.contents[0].text.strip()
            except Exception:
                return ""


# FUNCTION: Extract Tool + Arguments from LLM Output

# The LLM returns text that should contain JSON.
# This function extracts and parses that JSON safely.
def extract_tool_args(raw_text):

    # Remove comments (if any)
    clean_text = re.sub(r'//.*', '', raw_text)

    # Extract JSON object using regex
    match = re.search(r'\{.*\}', clean_text, re.DOTALL)

    if not match:
        print("No JSON object found in response.")
        return None, {}

    try:
        data = json.loads(match.group())
    except json.JSONDecodeError as e:
        print(f"Failed to parse JSON: {e}")
        return None, {}

    return data.get("tool"), data.get("args", {})


# FUNCTION: Classify User Message + Execute Tool

# This is the core logic:
# 1. Send user message to LLM (via MCP prompt)
# 2. Get tool name + arguments
# 3. Call the tool from MCP server
async def classify_and_execute(user_name: str, message: str) -> str:
    try:

        server_params = StdioServerParameters(
            command="uv",
            args=["run", "appointment_server.py"]
        )

        async with stdio_client(server_params) as (reader, writer):
            async with ClientSession(reader, writer) as session:

                await session.initialize()

                # Get prompt template from MCP server
                prompt = await session.get_prompt(
                    "appointment_prompt",
                    {"user_input": message}
                )

                prompt_text = prompt.messages[0].content.text

                # Send prompt to local LLM
                response = ollama.chat(
                    model="llama3.1-8b-local",
                    messages=[{"role": "system", "content": prompt_text}]
                )

                raw = response["message"]["content"].strip()

                # Extract tool and arguments from LLM output
                tool, args = extract_tool_args(raw)

                if not tool:
                    return "Sorry, I couldn't understand your request."

                args = (args or {})

                # Add required fields
                args["mobile"] = str(user_name)
                args["user_input"] = message

                # Call the MCP tool
                result = await session.call_tool(tool, args)

                return (result.content[0].text or "").strip()

    except Exception as e:
        return f"An error occurred while processing your request:\n{e}"


# FUNCTION: Handle Incoming Telegram Messages

# This function is triggered whenever a user sends a message.
# It extracts user info, processes the request, and sends a reply.
async def handle_message(update: Update, _context) -> None:

    # Ignore empty messages
    if not update.message or not update.message.text:
        return

    user_text = update.message.text.strip()

    # Build user identifier (used as mobile ID)
    first_name = update.effective_user.first_name or ""
    last_name = update.effective_user.last_name or ""
    full_name = (first_name + " " + last_name).strip()

    # Process request using MCP + LLM
    reply = await classify_and_execute(full_name, user_text)

    # Send reply back to user
    await update.message.reply_text(reply or "No response received from the service.")


# MAIN FUNCTION: Start Telegram Bot
async def main():
    try:
        # Get bot token dynamically from MCP server
        token = await get_token_from_mcp()

        if not token:
            raise RuntimeError("TELEGRAM_TOKEN not found.")

        # Build Telegram application
        app = ApplicationBuilder().token(token).build()

        # Handle only text messages (ignore commands like /start)
        app.add_handler(
            MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message)
        )

        # Start bot
        await app.initialize()
        await app.start()

        print("🤖 Bot is running... Press Ctrl+C to stop.")

        # Start polling updates from Telegram
        await app.updater.start_polling()

        # Keep program running
        await asyncio.Event().wait()

    except asyncio.CancelledError:
        print("Bot stopped.")


# Entry point
if __name__ == "__main__":
    asyncio.run(main())
