import asyncio
from mcp import ClientSession
#  هاي لانشاء session بين العميل والخادم
from mcp import StdioServerParameters
# هاي لتحديد كيفية تشغيل الخادم والطريقة الي راح يتواصل فيها مع العميل وهنستخدمها لتهيا الاتصال بين العميل والخادم عن طريق قنوات std in و std out
from mcp.client.stdio import stdio_client
import json
import ollama
import re

history = []

async def classify_user_input_with_server_prompt(session: ClientSession, history: list[dict]) -> dict:

    full_history = "\n".join([f"You: {msg['content']}" for msg in history if msg["role"] == "user"])

    try:
        prompt_result = await session.get_prompt("weather_classifier", {"natural_input": full_history})
    
        prompt_text = prompt_result.messages[0].content.text.strip()
    
    except Exception as e:
        print("❌ Error fetching prompt from server:", e)
        return {"tool": "none"}

    response = ollama.chat(
        model="llama3",
        messages=[{"role": "system", "content": prompt_text}] + history
    )

    raw = response["message"]["content"].strip()

    json_match = re.search(r'({.*})', raw)
    
    if not json_match:
        return {"tool": "none"}
    
    try:
        return json.loads(json_match.group(1))
    
    except:
        return {"tool": "none"}

async def main():
    server_params = StdioServerParameters(command="uv", args=["run", "weather_server_ollama.py"])
#  هلا هتبدا بتحديد كيف سيبدا العميل بتشغيل الخادممن خلال الامر uv  run وبعدها اسم الملف متبوعا بالامر 
#  يعني هادا بيعني انو العميل عند بدا تشغيله سيعمل على تشغيل خادم mcb كعملية فرعية sub process وسيتم التواصل معه عن طريق قنوات فرعية std in , std out 
#  هادا بيغنينا عن تشغيل الخادم يدويا 
    async with stdio_client(server_params) as (reader, writer):
        async with ClientSession(reader, writer) as session:
            await session.initialize()
            print("Weather Assistant Ready! (Type 'q' to quit)\n")

            while True:

                user_input = input("You: ").strip()
                
                if user_input.lower() in {"q", "quit", "exit"}:
                    print("Goodbye!")
                    break

                history.append({"role": "user", "content": user_input})

                parsed = await classify_user_input_with_server_prompt(session, history)

                if parsed.get("tool") == "get_current_weather":
                    args = parsed.get("args", {})
                    result = await session.call_tool("get_current_weather", args)
                    print("Weather Report:")
                    print(result.content[0].text.strip())
                    history.append({"role": "assistant", "content": result.content[0].text.strip()})

                elif parsed.get("tool") == "get_forecast":
                    args = parsed.get("args", {})
                    result = await session.call_tool("get_forecast", args)
                    print("Forecast Report:")
                    print(result.content[0].text.strip())
                    history.append({"role": "assistant", "content": result.content[0].text.strip()})

                else:
                    response = ollama.chat(
                        model="llama3",
                        messages=history
                    )
                    answer = response["message"]["content"].strip()
                    print("💬", answer)
                    history.append({"role": "assistant", "content": answer})

if __name__ == "__main__":
    asyncio.run(main())
