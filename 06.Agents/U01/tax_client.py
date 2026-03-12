import asyncio 
#بيطيب ليه بدنا نستخدم هاي لانو العمليات مع الخادم مش متزامنة بحيث بتدار بطريقة تسمح بتنفيذ مهام متعددة دون الحاجة للانتظار 

from mcp import ClientSession
from mcp import StdioServerParameters
from mcp.client.stdio import stdio_client
# هلا هاي مسؤؤولة عن فتح قناه بين العميل والخادم 
import json

async def main():
    server_params = StdioServerParameters(command="uv" , args=["run", "tax_server.py"])

    async with stdio_client(server_params) as (reader, writer):
        async with ClientSession(reader, writer) as session:
            await session.initialize()
            print("Connected to the server.")

            while True:
                print("=== Menu === ")
                print("1. Get Tax ")
                print("2. Tax Greeting ")
                print("3. View All VIT Settings ")
                print("4. Exit")

                choice = input("Enter your choice: ").strip()

                if choice == "1":
                    try :
                        price = float(input("Enter price: "))
                    except ValueError:
                        print("Invalid price. Please enter a valid number.")
                        continue
                    
                    country = input("Enter country: ").strip()
                    try:
                        tax_amount = await session.call_tool("calculate_tax",{ "income": price, "country": country })
                        print("Tax Rates:", tax_amount.content[0].text.strip())
                    except Exception as e:
                        print(f"Error occurred while fetching tax config: {e}")
                        continue
       

                elif choice == "2":
                    name = input("Enter name: ")
                    country = input("Enter country: ")
                    try:
                        greeting = await session.get_prompt("tax_greeting",{ "name": name, "country": country })
                        print(greeting.messages[0].content.text.strip())
                    except Exception as e:
                        print(f"Error occurred while fetching tax greeting: {e}")
                        continue
                    


                elif choice == "3":
                    resource_data = await session.read_resource("resources://tax_config")
                    resource_text =resource_data.contents[0].text.strip()
                    data = json.loads(resource_text)
                    print("\n Available VAT Settings:")
                    for key, value in data.items():
                        print(f"  {key}: {value}")

                elif choice == "4":
                    break

                else:
                    print("Invalid choice.")

if __name__ == "__main__":
    asyncio.run(main())
