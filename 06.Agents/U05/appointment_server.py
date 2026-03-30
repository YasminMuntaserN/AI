# Import MCP framework (used to expose tools/resources to AI agents like Claude)
from mcp.server.fastmcp import FastMCP

# Import your custom modules
import calendar_tools.calendar_functions as cal   # Google Calendar logic
import email_tools.email_functions as em          # Email sending logic
import db_tools.db_functions as db                # Database operations

# Standard Python libraries
import os
import sys
from dotenv import load_dotenv   # Load environment variables from .env file
import re                        # Regex for extracting emails
from typing import Optional
from ollama import chat          # Local LLM (llama3.1-8b-local)
from datetime import date

# Fix encoding for Arabic text output
sys.stdout.reconfigure(encoding='utf-8')

# Load environment variables
load_dotenv()

# Initialize MCP server with name "appointment"
mcp = FastMCP("appointment")


#  RESOURCES (CONFIG DATA)


# Google Calendar permissions
@mcp.resource("resource://calendar_scopes_resource")
def calendar_scopes_resource():
    return ["https://www.googleapis.com/auth/calendar"]


# Path to Google credentials file
@mcp.resource("resource://credentials_file_resource")
def credentials_file_resource():
    return "credentials.json"


# Path to Google token file (OAuth session)
@mcp.resource("resource://token_file_resource")
def token_file_resource():
    return "token.json"


# Email (SMTP) configuration
@mcp.resource("resource://smtp_settings_resource")
def smtp_settings_resource():
    return {
        "from": os.getenv("EMAIL_FROM"),
        "password": os.getenv("EMAIL_PASSWORD"),
        "server": os.getenv("SMTP_SERVER"),
        "port": int(os.getenv("SMTP_PORT", 587))
    }


# PostgreSQL basic connection config
@mcp.resource("resource://pg_config_resource")
def pg_config_resource():
    return {
        "user": os.getenv("DB_USER"),
        "password": os.getenv("DB_PASSWORD"),
        "host": os.getenv("DB_HOST"),
        "port": int(os.getenv("DB_PORT", 5432))
    }


# Database name
@mcp.resource("resource://db_name_resource")
def db_name_resource():
    return os.getenv("DB_NAME")


# Full DB config (includes db name)
@mcp.resource("resource://db_config_resource")
def db_config_resource():
    config = pg_config_resource().copy()
    config["dbname"] = os.getenv("DB_NAME")
    return config


# Timezone used for appointments
@mcp.resource("resource://timezone_resource")
def timezone_resource():
    return os.getenv("TIMEZONE", "Asia/Riyadh")


# Working hours configuration
@mcp.resource("resource://working_hours_resource")
def working_hours_resource():
    return {
        "start_hour": int(os.getenv("START_HOUR", 10)),
        "end_hour": int(os.getenv("END_HOUR", 17)),
        "interval_minutes": int(os.getenv("INTERVAL_MINUTES", 30))
    }


# Custom business info (used by AI responses)
@mcp.resource("resource://custom_data_snippet_resource")
def custom_data_snippet_resource():
    with open("center_data.txt", encoding="utf-8") as f:
        return f.read()


# Telegram bot token
@mcp.resource("resource://telegram_token_resource")
def telegram_token_resource():
    return os.getenv("TELEGRAM_TOKEN", "")



# HELPER FUNCTION

# Extract email from user text using regex
def extract_email_from_text(text: str) -> str:
    matches = re.findall(r"[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+", text)
    return matches[0] if matches else ""


#  TOOL: SCHEDULE APPOINTMENT

@mcp.tool(name="schedule_appointment_tool")
def schedule_appointment_tool(
    mobile: str,
    date: str,
    email: Optional[str] = None,
    user_input: Optional[str] = None
) -> str:

    try:
        answer = ""
        extracted = ""

        # Validate mobile number
        if not mobile or mobile.strip() == "":
            return "Please provide your mobile number."

        DB_CONFIG = db_config_resource()

        # Clean email input
        email = (email or "").strip()

        # If no email provided → try DB → then extract from text
        if email == "":
            db_email = db.get_email(mobile, DB_CONFIG)

            if db_email:
                email = db_email.strip()
            else:
                extracted = extract_email_from_text(user_input)
                if extracted:
                    email = extracted.strip()

        # Save or update customer info
        db.add_or_update_customer(mobile, email, DB_CONFIG)

        # Load configs
        tz_name = timezone_resource()
        SCOPES = calendar_scopes_resource()
        CREDENTIALS_FILE = credentials_file_resource()
        TOKEN_FILE = token_file_resource()
        working_hours = working_hours_resource()

        # Schedule appointment in Google Calendar
        answer = cal.schedule_appointment(
            mobile=mobile,
            date=date,
            tz_name=tz_name,
            SCOPES=SCOPES,
            CREDENTIALS_FILE=CREDENTIALS_FILE,
            TOKEN_FILE=TOKEN_FILE,
            start_hour=working_hours["start_hour"],
            end_hour=working_hours["end_hour"],
            minutes=working_hours["interval_minutes"]
        )

        # If email was extracted → inform user
        if email and extracted:
            answer += f"\nYour email has been updated: {email}"

        # Send confirmation email
        if email:
            try:
                smtp_settings = smtp_settings_resource()
                em.send_email(
                    to=email,
                    subject="Appointment Confirmation",
                    body=answer,
                    settings=smtp_settings
                )
            except Exception as e:
                answer += f"\n(Failed to send email: {e})"

        # Log conversation
        db.log_conversation(mobile, 'user', user_input, DB_CONFIG)
        db.log_conversation(mobile, 'assistant', answer, DB_CONFIG)

    except Exception as e:
        print(f"Error scheduling appointment: {e}")

    return answer


@mcp.tool(name="get_appointments_tool")
def get_appointments_tool(mobile: str, user_input: Optional[str] = None) -> str:

    try:
        if not mobile or mobile.strip() == "":
            return "Please provide your mobile number."

        # Get appointments from calendar
        answer = cal.get_appointments(
            mobile=mobile,
            SCOPES=calendar_scopes_resource(),
            CREDENTIALS_FILE=credentials_file_resource(),
            TOKEN_FILE=token_file_resource()
        )

        DB_CONFIG = db_config_resource()

        # Try extracting email
        email = extract_email_from_text(user_input or "")
        if email:
            db.add_or_update_customer(mobile, email, DB_CONFIG)
            answer += f"\nYour email has been updated: {email}"

        # Log conversation
        db.log_conversation(mobile, "user", user_input, DB_CONFIG)
        db.log_conversation(mobile, "assistant", answer, DB_CONFIG)

    except Exception as e:
        print(f"Error retrieving appointments: {e}")

    return answer


@mcp.tool(name="cancel_appointment_tool")
def cancel_appointment_tool(mobile: str, date: str, user_input: Optional[str] = None) -> str:
    try:
        if not mobile or mobile.strip() == "":
            return "Please provide your mobile number."

        # Cancel appointment
        answer = cal.cancel_appointment(
            mobile=mobile,
            date=date,
            SCOPES=calendar_scopes_resource(),
            CREDENTIALS_FILE=credentials_file_resource(),
            TOKEN_FILE=token_file_resource()
        )

        DB_CONFIG = db_config_resource()

        # Extract email if present
        email = extract_email_from_text(user_input or "")
        if email:
            db.add_or_update_customer(mobile, email, DB_CONFIG)
            answer += f"\nYour email has been updated: {email}"

        # Log conversation
        db.log_conversation(mobile, "user", user_input, DB_CONFIG)
        db.log_conversation(mobile, "assistant", answer, DB_CONFIG)

    except Exception as e:
        print(f"Error canceling appointment: {e}")

    return answer


@mcp.tool(name="default_response")
def default_response(user_input, mobile: Optional[str] = None) -> str:

    try:
        msg = "Welcome! This assistant helps you manage appointments."

        DB_CONFIG = db_config_resource()

        # Save user if exists
        if mobile:
            db.add_or_update_customer(mobile, "", DB_CONFIG)

        # Load business data
        MY_DATA = custom_data_snippet_resource()

        # Extract email
        email = extract_email_from_text(user_input)
        if email:
            db.add_or_update_customer(mobile, email, DB_CONFIG)
            msg += f"\nYour email has been updated: {email}"

        # AI prompt
        prompt = f"""
        Use the following info to answer:
        -------------------
        {MY_DATA}
        -------------------
        Answer in Arabic only, briefly, without inventing info.
        User message:
        {user_input}
        """

        # Call local LLM
        llm_response = chat(
            model="llama3.1-8b-local",
            messages=[{"role": "system", "content": prompt}]
        )

        msg += "\n\n" + llm_response["message"]["content"].strip()

        # Check if email missing
        if not email and db.check_missing_email(mobile, DB_CONFIG):
            msg += "\nPlease provide your email for confirmations."

        # Log conversation
        db.log_conversation(mobile, 'user', user_input, DB_CONFIG)
        db.log_conversation(mobile, 'assistant', msg, DB_CONFIG)

    except Exception as e:
        print(f"Error in default response: {e}")

    return msg

@mcp.prompt(
    name="appointment_prompt",
    description="Classify user message and call the appropriate tool in JSON format."
)
def appointment_prompt(user_input: str, today: str = str(date.today())):
    return f"""
You are an intelligent Arabic-speaking assistant. Your task is to understand the user's message and accurately classify it to call the correct tool.

Today's date: {today}

Available tools (ONLY these four):

----------------------------------------
1) Schedule Appointment
----------------------------------------
Use when the user wants to book an appointment on a specific date.

Tool: `schedule_appointment_tool`

Required:
- `date`: appointment date in format YYYY-MM-DD
- `mobile`: phone number

Optional:
- `email`: email address


----------------------------------------
2) Cancel Appointment
----------------------------------------
Use when the user wants to cancel an appointment on a specific date.

Tool: `cancel_appointment_tool`

Required:
- `date`: appointment date in format YYYY-MM-DD
- `mobile`: phone number


----------------------------------------
3) View Appointments
----------------------------------------
Use when the user asks to see their upcoming appointments.

Tool: `get_appointments_tool`

Required:
- `mobile`: phone number


----------------------------------------
4) General / Non-appointment Messages
----------------------------------------
Use when the message is unrelated to appointments (questions, greetings, etc.).

Tool: `default_response`

Required:
- `user_input`: the user's message


----------------------------------------
Instructions:
----------------------------------------

- Carefully analyze the user's message and select ONLY ONE of the four tools above.
- DO NOT return more than one JSON object.
- DO NOT assume or guess missing information.
- Convert relative dates (e.g., "next Thursday", "after one week") into YYYY-MM-DD format using today's date: {today}.
- Extract the email if it exists in the message.
- The output MUST be a valid JSON only (no explanations, no comments, no extra text).
- If the message only contains:
  - email → use `default_response`
  - greeting / goodbye → use `default_response`

----------------------------------------
User Message:
{user_input}

----------------------------------------
Expected Output:
----------------------------------------

- Output MUST be exactly ONE valid JSON object.
- It MUST match one of these tools only:
  `schedule_appointment_tool`, `cancel_appointment_tool`,
  `get_appointments_tool`, or `default_response`.

- DO NOT include any explanations or comments.

----------------------------------------
Examples:
----------------------------------------

Example (Schedule Appointment):
{{
  "tool": "schedule_appointment_tool",
  "args": {{
    "date": "2025-08-10",
    "mobile": "0551234567",
    "email": "example@email.com",
    "user_input": "Book me an appointment"
  }}
}}

Example (Cancel Appointment):
{{
  "tool": "cancel_appointment_tool",
  "args": {{
    "date": "2025-08-12",
    "mobile": "0551234567",
    "user_input": "Cancel my appointment"
  }}
}}

Example (View Appointments):
{{
  "tool": "get_appointments_tool",
  "args": {{
    "mobile": "0551234567",
    "user_input": "When are my appointments?"
  }}
}}

Example (General Question):
{{
  "tool": "default_response",
  "args": {{
    "user_input": "Where is your center located?",
    "mobile": "0551234567"
  }}
}}

----------------------------------------
Final Rules:
----------------------------------------

- If the message is unclear → use `default_response`.
- ALWAYS return exactly ONE JSON object.
- DO NOT write anything except the JSON.
"""


if __name__ == "__main__":

    # Get DB config
    DB_CONFIG = db_config_resource()

    # Create tables (ONLY for Supabase)
    db.create_tables(DB_CONFIG)

    # Start MCP server
    mcp.run(transport="stdio")

    DB_CONFIG = db_config_resource()

    db.create_tables(DB_CONFIG)

    mcp.run(transport="stdio")