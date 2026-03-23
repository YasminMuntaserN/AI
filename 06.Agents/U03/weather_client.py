import asyncio

from mcp import ClientSession
from mcp import StdioServerParameters
from mcp.client.stdio import stdio_client


async def main():

    # Configure how to start the MCP server
    # This means the client will launch the server as a subprocess
    # using "uv run weather_server.py"
    # Communication happens via stdin and stdout streams
    server_params = StdioServerParameters(
        command="uv",
        args=["run", "weather_server.py"]
    )

    # Start the stdio client and connect to the server
    async with stdio_client(server_params) as (reader, writer):

        # Create a session to interact with MCP tools
        async with ClientSession(reader, writer) as session:

            # Initialize the session (handshake with the server)
            await session.initialize()

            print("Connected to MCP Weather Server")

            while True:

                # Ask user for city name
                city = input("\nEnter city name (or 'q' to quit): ").strip()

                # Exit condition
                if city.lower() in {"q", "quit", "exit"}:
                    print("Goodbye!")
                    break

                # Ask user which operation to perform
                print("\nChoose an option:")
                print("1. Get current weather")
                print("2. Get 5-entry forecast")

                choice = input("Enter 1 or 2: ").strip()

                # Call MCP tool: get_current_weather
                if choice == "1":

                    result = await session.call_tool(
                        "get_current_weather",
                        {"city": city}
                    )

                    print("\nWeather Report:\n" +
                          result.content[0].text.strip())

                # Call MCP tool: get_forecast
                elif choice == "2":

                    result = await session.call_tool(
                        "get_forecast",
                        {"city": city}
                    )

                    print("\nForecast:\n" +
                          result.content[0].text.strip())

                # Handle invalid input
                else:
                    print("Invalid choice. Please enter 1 or 2.")


# Entry point of the client application
if __name__ == "__main__":
    asyncio.run(main())