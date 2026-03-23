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

 #هوا موجه برومت يخبر النموذج اللغوي انه عليه استخراج اسم البلد من النص المدخل من قبل المستخدم   OLLAMA  هلا الي بحتاجه لنتعامل مع نموذج لغوي من  
@mcp.prompt(name="tool_classifier", description="Classifies user input into tool call JSON for known tools.")
def tool_classifier(natural_input: str):
# natural_input النص المدخل من المستخدم 
    countries = list(tax_config().keys())

    country_list = ', '.join(f'"{c}"' for c in countries)

    return f"""
        You are an intelligent assistant that converts user questions into tool call JSON.

        Your goal is to:
        - Identify the correct tool to use (from registered tools)
        - Extract the arguments required for that tool
        - Ensure all argument values match the expected format

        Available tool:
        - Name: "calculate_tax"
        - Required arguments:
        - "price": a numeric value (float or int)
        - "country": must be one of: [{country_list}]

        Examples:
        - If the user says: "What is the tax on 1000 in UAE?" → Return: {{"tool": "calculate_tax", "args": {{"price": 1000, "country": "UAE"}}}}
        - If the user says: "What is the VAT on 2000 dirhams?" → You must infer "UAE" based on the word "dirhams"

        Guidelines:
        - You must always use the country names exactly as written in this list: [{country_list}]
        - If the country is not mentioned explicitly, try to infer it from context (e.g., currency terms like "riyals", "dirhams", "pounds", or location words like "Riyadh", "Dubai", "Cairo", etc.)
        - Always include both "price" and "country" in the response.
        - If either is missing or unclear, return: {{"tool": "none"}}
        - Try to infer the country from currency symbols if the country name is not clearly mentioned.
        For example:
            - SAR → Saudi Arabia
            - AED → UAE

        Output format:
        Respond with valid JSON only — no text, no explanation, no extra characters.

        Now process the following user input:

        "{natural_input}"
"""

if __name__ == "__main__":
    mcp.run(transport="stdio")