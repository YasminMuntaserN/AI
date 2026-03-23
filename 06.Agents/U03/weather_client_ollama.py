import asyncio
import json
import re
import ollama

from mcp import ClientSession
# Used to create a communication session between client and server

from mcp import StdioServerParameters
# Defines how the MCP server will be started and how communication happens

from mcp.client.stdio import stdio_client
# Handles communication via stdin/stdout streams


# Store conversation history (for context awareness)
history = []


# Function: classify user input using MCP prompt + LLM
async def classify_user_input_with_server_prompt(
    session: ClientSession,
    history: list[dict]
) -> dict:

    # Combine user messages into a single context string
    full_history = "\n".join(
        [f"You: {msg['content']}" for msg in history if msg["role"] == "user"]
    )

    try:
        # Fetch prompt template from MCP server
        prompt_result = await session.get_prompt(
            "weather_classifier",
            {"natural_input": full_history}
        )

        prompt_text = prompt_result.messages[0].content.text.strip()

    except Exception as e:
        print("❌ Error fetching prompt from server:", e)
        return {"tool": "none"}

    # Send prompt + conversation to LLM (Ollama)
    response = ollama.chat(
        model="llama3.1-8b-local",
        messages=[{"role": "system", "content": prompt_text}] + history
    )

    raw = response["message"]["content"].strip()

    # Extract JSON from model output
    json_match = re.search(r'({.*})', raw)

    if not json_match:
        return {"tool": "none"}

    try:
        return json.loads(json_match.group(1))
    except:
        return {"tool": "none"}


async def main():

    # Configure how the MCP server will be launched
    # The client will automatically start the server as a subprocess
    # using: uv run weather_server_ollama.py
    # Communication is done via stdin/stdout
    server_params = StdioServerParameters(
        command="uv",
        args=["run", "weather_server_ollama.py"]
    )

    # Start client-server connection
    async with stdio_client(server_params) as (reader, writer):
        async with ClientSession(reader, writer) as session:

            # Initialize MCP session
            await session.initialize()

            print("Weather Assistant Ready! (Type 'q' to quit)\n")

            while True:

                # Get user input
                user_input = input("You: ").strip()

                # Exit condition
                if user_input.lower() in {"q", "quit", "exit"}:
                    print("Goodbye!")
                    break

                # Add user input to conversation history
                history.append({"role": "user", "content": user_input})

                # Classify user input into tool call
                parsed = await classify_user_input_with_server_prompt(session, history)

                # If tool = current weather
                if parsed.get("tool") == "get_current_weather":

                    args = parsed.get("args", {})

                    result = await session.call_tool(
                        "get_current_weather", args
                    )

                    response_text = result.content[0].text.strip()

                    print("Weather Report:")
                    print(response_text)

                    history.append({"role": "assistant", "content": response_text})

                # If tool = forecast
                elif parsed.get("tool") == "get_forecast":

                    args = parsed.get("args", {})

                    result = await session.call_tool(
                        "get_forecast", args
                    )

                    response_text = result.content[0].text.strip()

                    print("Forecast Report:")
                    print(response_text)

                    history.append({"role": "assistant", "content": response_text})

                # If no tool matched → fallback to LLM chat
                else:

                    response = ollama.chat(
                        model="llama3.1-8b-local",
                        messages=history
                    )

                    answer = response["message"]["content"].strip()

                    print("💬", answer)

                    history.append({"role": "assistant", "content": answer})


# Entry point
if __name__ == "__main__":
    asyncio.run(main())