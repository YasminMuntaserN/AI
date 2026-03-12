from mcp.server.fastmcp import FastMCP
# هلا هادا FastMCP لتشغيل خادم MCP دون الحاجة لاعدادات معقدة 
import httpx
# httpx مكتبة قوية لارسال طلبات HTTP بشكل غير متزامن 
from typing import Any

mcp = FastMCP("weather") # كائن الخادم 

@mcp.resource("resource://weather_config_resource") 
# هلا جوا المصدر هنعرف دالة هترجع قاموس هيتحتوي ال URL ومفتاح الوصول
def weather_config_resource():
    return {
        "base_url": "https://api.openweathermap.org/data/2.5",
        "api_key": "b5508458add2167a49c596cba069e2f1"
    }


# هلا هاي لارسال الطلب لللاستفسار عن الطلب 
async def make_owm_request(
    endpoint: str,
    params: dict[str, Any], # هنمرر اسم المدينة 
    weather_config: dict[str, Any]
) -> dict[str, Any] | None:

    weather_config=weather_config_resource()# هلا هاي الدالة هتصل لاعدادات الدالة 
    base_url = weather_config.get("base_url")
    api_key = weather_config.get("api_key")

    if not api_key: # اذا المفاتح مش موجود 
        print("[ERROR] Missing OpenWeatherMap API key.")
        return None

    params["appid"] = api_key
    params["units"] = "metric" # هاي للحصول على درجات الحرارة بالدرجة المئوية 

    try:
        async with httpx.AsyncClient() as client:
            url = f"{base_url}/{endpoint}"
            
            print(f"[INFO] Requesting: {url} with params {params}")
            
            response = await client.get(url, params=params, timeout=30.0)

            response.raise_for_status() 

            return response.json()       
    
    except Exception as e:
        print(f"[ERROR] OpenWeatherMap request failed: {e}")
        return None

@mcp.tool()
async def get_current_weather(city: str, weather_config: dict[str, Any] = None) -> str:

    if weather_config is None: # اذا ما تمررت هنجيبها
        weather_config=weather_config_resource()

    data = await make_owm_request(endpoint="weather", params={"q": city}, weather_config=weather_config)
    if not data: # هلا من الجيسون الي هيرجع بدنا نستخرج المعلومات 
        return f"ERROR: Could not retrieve current weather for '{city}'."

    """
    http://api.openweathermap.org/data/2.5/weather?q=Riyadh&appid=b5508458add2167a49c596cba069e2f1&units=metric
    خلا شو ممكن يرجع هادا الجيسون 
    {"coord":{"lon":46.7219,"lat":24.6877},"weather":[{"id":804,"main":"Clouds","description":"overcast clouds","icon":"04n"}],"base":"stations","main":{"temp":21.45,"feels_like":21.09,"temp_min":21.45,"temp_max":21.45,"pressure":1014,"humidity":55,"sea_level":1014,"grnd_level":942},"visibility":10000,"wind":{"speed":4.19,"deg":82,"gust":7.04},"clouds":{"all":99},"dt":1773341053,"sys":{"country":"SA","sunrise":1773284738,"sunset":1773327627},"timezone":10800,"id":108410,"name":"Riyadh","cod":200}
    هلا احنا شو هيلزمنا منو ؟ 
    الحالة الاساسية main 
    وسرعة الريح wind 
    ومعلومات زي اسم المدينو من ال sys = system 

    """
    main = data.get("main", {})

    weather = data.get("weather", [{}])[0]

    wind = data.get("wind", {})

    sys = data.get("sys", {})
 
    city_name = data.get("name", city) # اسم المدينة 

    country = sys.get("country", "")# اسم البلد 

    temperature = main.get("temp", "?")# درجة الحرارة 

    humidity = main.get("humidity", "?") # الرطوبة 

    wind_speed = wind.get("speed", "?")

    description = weather.get("description", "N/A").capitalize() # وصف لتوصيف حالة الطقس في بلد محددة 

    return (
        f"Current Weather in {city_name}, {country}:\n"
        f"Temperature: {temperature}°C\n"
        f"Humidity: {humidity}%\n"
        f"Wind: {wind_speed} m/s\n"
        f"Outlook: {description}"
    )

#  هلا هاي الاداة هتعيد لنا نص يشرح لنا التنبؤات في الايام القادمة 
@mcp.tool()
async def get_forecast(city: str, weather_config: dict[str, Any] = None) -> str:

    if weather_config is None:
        weather_config = weather_config_resource() # اذا ما تم تمريرها هنجيبها 

    """
    هلا لهادا هيكون هادا الرابط # http://api.openweathermap.org/data/2.5/forecast?q=Riyadh&appid=b5508458add2167a49c596cba069e2f1&units=metric 
    وهترجع اشي زي هيك :
    {"cod":"200","message":0,"cnt":40,"list":[{"dt":1773349200,"main":{"temp":21.42,"feels_like":21.11,"temp_min":18.77,"temp_max":21.42,"pressure":1014,"sea_level":1014,"grnd_level":944,"humidity":57,"temp_kf":2.65},"weather":[{"id":500,"main":"Rain","description":"light rain","icon":"10n"}],"clouds":{"all":66},"wind":{"speed":6.35,"deg":307,"gust":5.74},"visibility":9677,"pop":0.99,"rain":{"3h":1.62},"sys":{"pod":"n"},"dt_txt":"2026-03-12 21:00:00"},{"dt":1773360000,"main":{"temp":20.24,"feels_like":19.94,"temp_min":18.98,"temp_max":20.24,"pressure":1012,"sea_level":1012,"grnd_level":941,"humidity":62,"temp_kf":1.26},"weather":[{"id":500,"main":"Rain","description":"light rain","icon":"10n"}],"clouds":{"all":82},"wind":{"speed":5.7,"deg":139,"gust":9.81},"visibility":10000,"pop":1,"rain":{"3h":0.54},"sys":{"pod":"n"},"dt_txt":"2026-03-13 00:00:00"},{"dt":1773370800,"main":{"temp":17.84,"feels_like":17.59,"temp_min":17.84,"temp_max":17.84,"pressure":1014,"sea_level":1014,"grnd_level":942,"humidity":73,"temp_kf":0},"weather":[{"id":802,"main":"Clouds","description":"scattered clouds","icon":"03n"}],"clouds":{"all":25},"wind":{"speed":5.65,"deg":164,"gust":10.38},"visibility":10000,"pop":0,"sys":{"pod":"n"},"dt_txt":"2026-03-13 03:00:00"},{"dt":1773381600,"main":{"temp":21.91,"feels_like":21.51,"temp_min":21.91,"temp_max":21.91,"pressure":1014,"sea_level":1014,"grnd_level":943,"humidity":52,"temp_kf":0},"weather":[{"id":801,"main":"Clouds","description":"few clouds","icon":"02d"}],"clouds":{"all":16},"wind":{"speed":5.8,"deg":166,"gust":6.97},"visibility":10000,"pop":0,"sys":{"pod":"d"},"dt_txt":"2026-03-13 06:00:00"},{"dt":1773392400,"main":{"temp":27.38,"feels_like":26.75,"temp_min":27.38,"temp_max":27.38,"pressure":1012,"sea_level":1012,"grnd_level":942,"humidity":32,"temp_kf":0},"weather":[{"id":800,"main":"Clear","description":"clear sky","icon":"01d"}],"clouds":{"all":0},"wind":{"speed":3.07,"deg":235,"gust":4.62},"visibility":10000,"pop":0,"sys":{"pod":"d"},"dt_txt":"2026-03-13 09:00:00"},{"dt":1773403200,"main":{"temp":29.26,"feels_like":27.92,"temp_min":29.26,"temp_max":29.26,"pressure":1010,"sea_level":1010,"grnd_level":939,"humidity":27,"temp_kf":0},"weather":[{"id":801,"main":"Clouds","description":"few clouds","icon":"02d"}],"clouds":{"all":20},"wind":{"speed":3.84,"deg":294,"gust":4.63},"visibility":10000,"pop":0,"sys":{"pod":"d"},"dt_txt":"2026-03-13 12:00:00"},{"dt":1773414000,"main":{"temp":27.28,"feels_like":26.68,"temp_min":27.28,"temp_max":27.28,"pressure":1010,"sea_level":1010,"grnd_level":940,"humidity":32,"temp_kf":0},"weather":[{"id":803,"main":"Clouds","description":"broken clouds","icon":"04d"}],"clouds":{"all":58},"wind":{"speed":2.63,"deg":86,"gust":3.22},"visibility":10000,"pop":0,"sys":{"pod":"d"},"dt_txt":"2026-03-13 15:00:00"},{"dt":1773424800,"main":{"temp":25.88,"feels_like":25.44,"temp_min":25.88,"temp_max":25.88,"pressure":1013,"sea_level":1013,"grnd_level":942,"humidity":35,"temp_kf":0},"weather":[{"id":802,"main":"Clouds","description":"scattered clouds","icon":"03n"}],"clouds":{"all":44},"wind":{"speed":2.8,"deg":119,"gust":2.79},"visibility":10000,"pop":0,"sys":{"pod":"n"},"dt_txt":"2026-03-13 18:00:00"},{"dt":1773435600,"main":{"temp":22.81,"feels_like":22.45,"temp_min":22.81,"temp_max":22.81,"pressure":1013,"sea_level":1013,"grnd_level":942,"humidity":50,"temp_kf":0},"weather":[{"id":804,"main":"Clouds","description":"overcast clouds","icon":"04n"}],"clouds":{"all":100},"wind":{"speed":6.8,"deg":28,"gust":10.06},"visibility":10000,"pop":0,"sys":{"pod":"n"},"dt_txt":"2026-03-13 21:00:00"},{"dt":1773446400,"main":{"temp":20.24,"feels_like":19.63,"temp_min":20.24,"temp_max":20.24,"pressure":1013,"sea_level":1013,"grnd_level":942,"humidity":50,"temp_kf":0},"weather":[{"id":804,"main":"Clouds","description":"overcast clouds","icon":"04n"}],"clouds":{"all":100},"wind":{"speed":6.06,"deg":33,"gust":9.99},"visibility":10000,"pop":0,"sys":{"pod":"n"},"dt_txt":"2026-03-14 00:00:00"},{"dt":1773457200,"main":{"temp":18.95,"feels_like":18.49,"temp_min":18.95,"temp_max":18.95,"pressure":1015,"sea_level":1015,"grnd_level":943,"humidity":61,"temp_kf":0},"weather":[{"id":803,"main":"Clouds","description":"broken clouds","icon":"04n"}],"clouds":{"all":71},"wind":{"speed":3.66,"deg":73,"gust":7.02},"visibility":10000,"pop":0,"sys":{"pod":"n"},"dt_txt":"2026-03-14 03:00:00"},{"dt":1773468000,"main":{"temp":22.21,"feels_like":21.84,"temp_min":22.21,"temp_max":22.21,"pressure":1016,"sea_level":1016,"grnd_level":945,"humidity":52,"temp_kf":0},"weather":[{"id":802,"main":"Clouds","description":"scattered clouds","icon":"03d"}],"clouds":{"all":36},"wind":{"speed":6.13,"deg":107,"gust":7.7},"visibility":10000,"pop":0,"sys":{"pod":"d"},"dt_txt":"2026-03-14 06:00:00"},{"dt":1773478800,"main":{"temp":26.62,"f
    """
    data = await make_owm_request(endpoint="forecast", params={"q": city}, weather_config=weather_config)
    if not data or "list" not in data:
        return f"ERROR: Unable to fetch forecast for '{city}'."

    city_info = data.get("city", {})

    forecasts = []

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

if __name__ == "__main__":
    mcp.run(transport="stdio")