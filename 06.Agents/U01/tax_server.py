from mcp.server.fastmcp import FastMCP

mcp = FastMCP("TaxAssistant")

@mcp.resource("resources://tax_config")
def tax_config():
    return {
        "Saudi Arabia": 15,
        "United States": 10,
        "United Kingdom": 20,   
        "Germany": 19,
        "France": 20,
        "Japan": 10,
        "Australia": 10,
    }

@mcp.tool(name ="calculate_tax")
def calculate_tax(income: float, country: str) -> float:
    tax_rates = tax_config()
    tax_rate = tax_rates.get(country)
    if tax_rate is None:
        raise ValueError(f"Tax rate for {country} not found.")
    tax_amount = income * (tax_rate / 100)
    return round(tax_amount, 2)


@mcp.prompt(name="tax_greeting" , description="Greet the user and with VAT information")
def tax_greeting(name : str ,country: str):
    config = tax_config()
    config_lower = {k.lower(): v for k, v in config.items()}
    country_key = country.lower()

    if country_key in config_lower:
        tax_rate = config_lower[country_key]
        return f"Hello {name}! The VAT rate for {country} is {tax_rate}%."
    else:
        return f"Sorry {name}, I don't have VAT information for {country}."
    
if __name__ == "__main__":
    mcp.run(transport="stdio")