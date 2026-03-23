import asyncio
from mcp import ClientSession
from mcp import StdioServerParameters
from mcp.client.stdio import stdio_client
import json
import ollama

history = [
    {"role": "system", 
     "content": "You are a helpful assistant that can calculate taxes and answer general questions."}
]

last_tool_args = {}  

async def classify_tool_call(session, natural_input: str, full_history: list) -> dict:
    try:
        prompt_result = await session.get_prompt("tool_classifier", {
            "natural_input": natural_input
        })
        
        prompt_text = prompt_result.messages[0].content.text.strip()
    
    except Exception as e:
        print("Error fetching prompt from server:", e)
        return {"tool": "none"}

    try:
        messages = [{"role": "system", "content": prompt_text}]
        recent_messages = [msg for msg in full_history[-4:] if msg["role"] in {"user", "assistant"}]
        messages.extend(recent_messages)
        messages.append({"role": "user", "content": natural_input})
        response =  ollama.chat(
            model="llama3.1-8b-local",
            messages=messages
        )

        try:
            return json.loads(response["message"]["content"])
        
        except json.JSONDecodeError:
            print("SON parsing failed.")
            return {"tool": "none"}
    
    except Exception as e:
        print("Ollama failed to parse:", e)
        return {"tool": "none"}

async def answer_general_question(user_input: str) -> str:
    global history

    try:
        response =  ollama.chat(
            model="llama3.1-8b-local",
            messages=history
        )

        answer = response["message"]["content"]
        history.append({"role": "assistant", "content": answer})

        return answer

    except Exception as e:
        return f"Failed to answer with Ollama: {e}"

async def main():

    global last_tool_args  

    server_params = StdioServerParameters(command="python", args=["tax_server_ollama.py"])

    async with stdio_client(server_params) as (reader, writer):
        async with ClientSession(reader, writer) as session:

            await session.initialize()  
            print("Ready! Ask something like: 'What is the tax on 500 in KSA?' or ask general questions.")

            while True:
                user_input = input("\nYou: ").strip()

                if user_input.lower() in {"q", "quit", "exit"}:
                    print("Exiting.")
                    break

                history.append({"role": "user", "content": user_input})

                parsed = await classify_tool_call(session, user_input, history)

                if parsed.get("tool", "").lower() == "calculate_tax":
                    args = parsed.get("args", {})

                    last_tool_args.update(args)

                    try:
                        result = await session.call_tool("calculate_tax", last_tool_args)
                        output = result.content[0].text.strip()
                        print(f"Tax Result: {output}")
                        history.append({"role": "assistant", "content": output})
                    
                    except Exception as e:
                        error_msg = f"Error calling tool: {e}"
                        print(error_msg)
                        history.append({"role": "assistant", "content": error_msg})
                
                else:
                    response = await answer_general_question(user_input)
                    print(f"{response}")

                    history.append({"role": "assistant", "content": response})
                    last_tool_args = {}


if __name__ == "__main__":
    asyncio.run(main())
