# Import all tools and resources from the weather server
# This allows us to reuse the MCP server instance and tools
from weather_server import *

# MCP Prompt (LLM instruction)
@mcp.prompt(
    name="weather_classifier",
    description="Classifies natural user input into a weather tool call JSON using conversation context."
)
def weather_classifier_prompt(natural_input: str):
    return f"""
You are a helpful AI that converts multi-turn user conversations into structured tool calls.

Available tools:
- get_current_weather(city: str)
- get_forecast(city: str)

Instructions:
- Use previous conversation turns to understand references like "tomorrow", "there", or "that city".
- Always extract the most relevant city and map it to a tool.
- Only respond with a valid JSON like one of the following examples.

Examples:
Q: What's the weather like in Cairo today?
→ {{"tool": "get_current_weather", "args": {{"city": "Cairo"}}}}

Q: I want the forecast for Rome.
→ {{"tool": "get_forecast", "args": {{"city": "Rome"}}}}

If you can't extract a valid tool and city, respond with:
{{"tool": "none"}}

Conversation so far:
{natural_input}
"""

# Start MCP server
if __name__ == "__main__":
    mcp.run(transport="stdio")