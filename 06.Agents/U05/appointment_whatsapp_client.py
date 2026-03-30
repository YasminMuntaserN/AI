# appointment_whatsapp_client.py
from flask import Flask, request, Response
from twilio.rest import Client
from twilio.twiml.messaging_response import MessagingResponse

import asyncio
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

import json
import ollama
import re
from pyngrok import ngrok, conf
from threading import Thread
import os

# -----------------------------
# Environment / Config
# -----------------------------
TWILIO_ACCOUNT_SID = os.environ.get("TWILIO_ACCOUNT_SID")
TWILIO_AUTH_TOKEN = os.environ.get("TWILIO_AUTH_TOKEN")
TWILIO_SANDBOX_NUMBER = "whatsapp:+14155238886"  # Twilio sandbox number

OLLAMA_MODEL = "llama3.1-8b-local"

app = Flask(__name__)

# -----------------------------
# Utilities
# -----------------------------
def clean_message(text: str) -> str:
    """Remove emojis, control chars, normalize spaces."""
    text = re.sub(r'[\U0001F300-\U0001FAFF]', '', text)
    text = re.sub(r'[\x00-\x1F\x7F-\x9F]', '', text)
    text = re.sub(r'\s+', ' ', text).strip()
    return text

def extract_tool_args(raw_text):
    """Extract JSON tool call from LLM response."""
    clean_text = re.sub(r'//.*', '', raw_text)
    match = re.search(r'\{.*\}', clean_text, re.DOTALL)
    if not match:
        print("❌ No JSON object found in LLM response.")
        return None, {}
    try:
        data = json.loads(match.group())
    except json.JSONDecodeError as e:
        print(f"❌ JSON parsing failed: {e}")
        return None, {}
    return data.get("tool"), data.get("args", {})

# -----------------------------
# MCP + Ollama Logic
# -----------------------------
async def classify_and_execute(mobile: str, message: str) -> str:
    try:
        server_params = StdioServerParameters(
            command="uv",
            args=["run", "appointment_server.py"]
        )
        async with stdio_client(server_params) as (reader, writer):
            async with ClientSession(reader, writer) as session:
                await session.initialize()

                # Get prompt from MCP
                prompt = await session.get_prompt(
                    "appointment_prompt",
                    {"user_input": message}
                )
                prompt_text = prompt.messages[0].content.text

                # Call local LLM
                response = ollama.chat(
                    model=OLLAMA_MODEL,
                    messages=[{"role": "system", "content": prompt_text}]
                )
                raw = response["message"]["content"].strip()

                # Extract tool
                tool, args = extract_tool_args(raw)
                args = args or {}
                args["mobile"] = mobile.replace("whatsapp:", "")
                args["user_input"] = message

                if tool and tool != "default_response":
                    result = await session.call_tool(tool, args)
                    return result.content[0].text.strip()
                else:
                    return "This bot is for appointment booking. Please provide your request clearly."
    except Exception as e:
        return f"❌ Error: {str(e)}"

# -----------------------------
# Flask Webhook
# -----------------------------
@app.route("/webhook", methods=["POST"])
def webhook():
    text = request.values.get("Body", "") or ""
    mobile = request.values.get("From", "") or ""
    print(f"📩 Incoming message: {text} from {mobile}")

    result = asyncio.run(classify_and_execute(mobile, text))
    cleaned = clean_message(result)

    resp = MessagingResponse()
    resp.message(cleaned)
    print(f"📤 Replying with: {cleaned}")
    return Response(resp.to_xml(), mimetype="application/xml")

# -----------------------------
# Run Flask
# -----------------------------
def run_flask():
    app.run(host="0.0.0.0", port=5000)

# -----------------------------
# Ngrok + Twilio Setup
# -----------------------------
def start_ngrok_and_update_twilio():
    conf.get_default().ngrok_path = "C:\\ngrok\\ngrok.exe"  # Path to ngrok.exe
    ngrok.kill()  # Stop existing sessions
    tunnel = ngrok.connect(5000)
    public_url = tunnel.public_url
    print(f"\n✅ WhatsApp Webhook URL: {public_url}/webhook\n")

    # Update Twilio sandbox webhook
    client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)
    try:
        sandbox = client.chat.services.list()[0]  # v1.services list fallback
    except Exception:
        sandbox = None

    if sandbox:
        sandbox.update(inbound_webhook_url=f"{public_url}/webhook")
        print("✅ Twilio sandbox webhook updated.")
    else:
        print("⚠️ Could not find Twilio sandbox service. Make sure sandbox is joined.")

    return public_url

# -----------------------------
# Main
# -----------------------------
if __name__ == "__main__":
    start_ngrok_and_update_twilio()
    Thread(target=run_flask, daemon=True).start()
    print("🚀 Bot is running... Press Enter to stop.")
    input()