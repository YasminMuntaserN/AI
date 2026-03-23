from mcp.server.fastmcp import FastMCP
# FastMCP is used to quickly create and run an MCP server without complex setup

import httpx
# httpx is a powerful library for making asynchronous HTTP requests

from typing import Any

import os

# Initialize MCP server instance
mcp = FastMCP("weather")

@mcp.resource("resource://weather_config_resource")
# This resource returns configuration for the weather API
# It includes the base URL and the API key
def weather_config_resource():
    return {
        "base_url": "https://api.openweathermap.org/data/2.5",
        "api_key": "b5508458add2167a49c596cba069e2f1"
    }


# Helper function to send requests to OpenWeatherMap API
async def make_owm_request(
    endpoint: str,
    params: dict[str, Any],  # Parameters like city name
    weather_config: dict[str, Any]
) -> dict[str, Any] | None:

    # Load configuration (base_url + api_key)
    weather_config = weather_config_resource()

    base_url = weather_config.get("base_url")
    api_key = weather_config.get("api_key")

    # Validate API key
    if not api_key:
        print("[ERROR] Missing OpenWeatherMap API key.")
        return None

    # Add required API parameters
    params["appid"] = api_key
    params["units"] = "metric"  # Return temperature in Celsius

    try:
        async with httpx.AsyncClient() as client:
            url = f"{base_url}/{endpoint}"

            print(f"[INFO] Requesting: {url} with params {params}")

            response = await client.get(url, params=params, timeout=30.0)

            # Raise error if request failed
            response.raise_for_status()

            return response.json()

    except Exception as e:
        print(f"[ERROR] OpenWeatherMap request failed: {e}")
        return None


@mcp.tool()
# Tool to get current weather for a given city
async def get_current_weather(city: str, weather_config: dict[str, Any] = None) -> str:

    # If config is not passed, load it
    if weather_config is None:
        weather_config = weather_config_resource()

    data = await make_owm_request(
        endpoint="weather",
        params={"q": city},
        weather_config=weather_config
    )

    # If no data returned
    if not data:
        return f"ERROR: Could not retrieve current weather for '{city}'."

    """
    Example API response:
    http://api.openweathermap.org/data/2.5/weather?q=Riyadh&appid=API_KEY&units=metric

    We extract:
    - Temperature (main.temp)
    - Humidity (main.humidity)
    - Weather description (weather.description)
    - Wind speed (wind.speed)
    - City and country info
    """

    main = data.get("main", {})
    weather = data.get("weather", [{}])[0]
    wind = data.get("wind", {})
    sys = data.get("sys", {})

    city_name = data.get("name", city)  # City name
    country = sys.get("country", "")    # Country code

    temperature = main.get("temp", "?")
    humidity = main.get("humidity", "?")
    wind_speed = wind.get("speed", "?")

    # Capitalize description for better readability
    description = weather.get("description", "N/A").capitalize()

    return (
        f"Current Weather in {city_name}, {country}:\n"
        f"Temperature: {temperature}°C\n"
        f"Humidity: {humidity}%\n"
        f"Wind: {wind_speed} m/s\n"
        f"Outlook: {description}"
    )


@mcp.tool()
# Tool to get weather forecast (next few time points)
async def get_forecast(city: str, weather_config: dict[str, Any] = None) -> str:

    # Load config if not provided
    if weather_config is None:
        weather_config = weather_config_resource()

    """
    Example API:
    http://api.openweathermap.org/data/2.5/forecast?q=City&appid=API_KEY&units=metric

    Returns multiple time-based forecasts (every ~3 hours).
    We will extract:
    - Timestamp
    - Temperature
    - Wind speed
    - Weather description
    """

    data = await make_owm_request(
        endpoint="forecast",
        params={"q": city},
        weather_config=weather_config
    )

    if not data or "list" not in data:
        return f"ERROR: Unable to fetch forecast for '{city}'."

    city_info = data.get("city", {})
    forecasts = []

    # Take first 5 forecast entries
    for entry in data["list"][:5]:

        main = entry.get("main", {})
        weather_info = entry.get("weather", [{}])[0]
        wind = entry.get("wind", {})

        timestamp = entry.get("dt_txt", "")
        temp = main.get("temp", "?")
        wind_speed = wind.get("speed", "?")

        description = weather_info.get("description", "N/A").capitalize()

        forecast_text = (
            f"{timestamp}:\n"
            f"Temperature: {temp}°C\n"
            f"Wind: {wind_speed} m/s\n"
            f"Outlook: {description}\n"
        )

        forecasts.append(forecast_text)

    city_name = city_info.get("name", city)
    country = city_info.get("country", "")

    header = f"City: {city_name}, {country}"

    return header + "\n" + "\n---\n".join(forecasts)


# Entry point for MCP server
if __name__ == "__main__":
    mcp.run(transport="stdio")