# مكتبة للعمليات غير المتزامنة
import asyncio

# جلسة اتصال مع MCP server
from mcp import ClientSession

# إعدادات تشغيل السيرفر
from mcp import StdioServerParameters

# إنشاء اتصال stdio
from mcp.client.stdio import stdio_client

# لتحويل النصوص JSON إلى dictionary
import json


async def main():

    # تحديد طريقة تشغيل الخادم
        # هلا هنا بنصرح انو الخادم هيتم تشغيله باستتخدام الامر uv run tax_server.py  
    #  وهادا بيعني انو العميل لما نشغله راح يقوم بتشغيل عميلة فرعية وراح يتم التواصل معو عبر قنوات std in ., std out  mcp
#  وهيك ما بنضطر نشغل السيرفر يدويا 

    server_params = StdioServerParameters(
        command="uv",
        args=["run", "tax_server.py"]
    )

    # فتح اتصال مع السيرفر
    async with stdio_client(server_params) as (reader, writer):

        # إنشاء جلسة اتصال
        async with ClientSession(reader, writer) as session:

            # تهيئة الاتصال
            await session.initialize()

            print("Connected to the server. \n")

            # حلقة تفاعلية
            while True:

                print("=== Menu ===")
                print("1. Get Tax (Calculate Tax)")
                print("2. Tax Greeting")
                print("3. View All VAT Settings")
                print("4. Exit")

                choice = input("Enter your choice (1-4): ").strip()

                # حساب الضريبة
                if choice == "1":

                    try:
                        price = float(input("Enter price: "))
                    except ValueError:
                        print("Invalid price , please enter a valid number.")
                        continue

                    country = input("Enter country: ").strip()

                    try:
                        tax_amount = await session.call_tool(
                            "calculate_tax",
                            {
                                "price": price,
                                "country": country
                            }
                        )

                        print("Calculated Tax:", tax_amount.content[0].text.strip())

                    except Exception as e:
                        print("Error:", e)

                # عرض رسالة ترحيب
                elif choice == "2":

                    name = input("Enter name: ").strip()
                    country = input("Enter country: ").strip()

                    greeting = await session.get_prompt(
                        "tax_greeting",
                        {
                            "name": name,
                            "country": country
                        }
                    )

                    print(greeting.messages[0].content.text.strip())


                # قراءة المورد
                elif choice == "3":

                    resource_data = await session.read_resource(
                        "resource://tax_config"
                    )

                    resource_text = resource_data.contents[0].text.strip()

                    data = json.loads(resource_text)

                    print("\nAvailable VAT Settings:")

                    for key, value in data.items():
                        print(f" - {key}: {value} %")

                elif choice == "4":
                    print("Goodbye!")
                    break

                else:
                    print("Invalid choice")

if __name__ == "__main__":
    asyncio.run(main())
