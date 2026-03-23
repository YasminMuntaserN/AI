from mcp.server.fastmcp import FastMCP

mcp = FastMCP("TaxAssistant")

@mcp.resource("resource://tax_config")
def tax_config():
    return {
        "Saudi Arabia": 15,
        "KSA": 15,
        "Saudi": 15,
        "UAE": 5,
        "United Arab Emirates": 5,
        "EGYPT": 14,
        "GERMANY": 19
    }

@mcp.tool(name="calculate_tax")
def calculate_tax(price: float, country: str) -> float:
    config = tax_config()
    
    config_lower = {k.lower(): v for k, v in config.items()}

    country_key = country.strip().lower()

    if country_key not in config_lower:
        raise ValueError(f"Country '{country}' not supported. Available: {list(config_lower.keys())}")

    tax_rate = config_lower[country_key]
    tax_amount = price * tax_rate / 100
    return round(tax_amount, 2)

@mcp.prompt(
    name="tax_greeting",
    description="Greet the user and show VAT information"
)
def tax_greeting(name: str, country: str):
    """
    موجه لغوي يقوم بتحية المستخدم
    وإظهار نسبة الضريبة للدولة
    """

    # قراءة بيانات الضريبة
    config = tax_config()

    # تحويل المفاتيح إلى lowercase
    config_lower = {k.lower(): v for k, v in config.items()}

    country_key = country.lower()

    # إذا كانت الدولة موجودة
    if country_key in config_lower:
        tax_rate = config_lower[country_key]

        return f"Hello {name}! The VAT rate for {country} is {tax_rate}%."

    # إذا لم تكن موجودة
    else:
        return f"Sorry {name}, I don't have VAT information for {country}."


if __name__ == "__main__":
    mcp.run(transport="stdio")