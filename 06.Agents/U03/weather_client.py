import asyncio

from mcp import ClientSession

from mcp import StdioServerParameters

from mcp.client.stdio import stdio_client

async def main():

    server_params = StdioServerParameters(command="uv", args=["run", "weather_server.py"]) 
    # هلا هادا السطر بيعني انو العميل لما نشغله هيقوم بتشيل الخادم بعملية فرعية subprocess وراح يتم التعامل معو عن طريق قنوات فرعية std in , std out 

    async with stdio_client(server_params) as (reader, writer):
        async with ClientSession(reader, writer) as session:
            await session.initialize()
            print("Connected to MCP Weather Server")

            while True:

                city = input("\nEnter city name (or 'q' to quit): ").strip()
                if city.lower() in {"q", "quit", "exit"}:
                    print("Goodbye!")
                    break

                print("\nChoose an option:")
                print("1. Get current weather")
                print("2. Get 5-entry forecast")
                choice = input("Enter 1 or 2: ").strip()

                if choice == "1":

                    result = await session.call_tool("get_current_weather", {"city": city})
                    print("\nWeather Report:\n" + result.content[0].text.strip())

                elif choice == "2":

                    result = await session.call_tool("get_forecast", {"city": city})
                    print("\nForecast:\n" + result.content[0].text.strip())

                else:
                    print("Invalid choice. Please enter 1 or 2.")

if __name__ == "__main__":
    asyncio.run(main())