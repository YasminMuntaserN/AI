# OAuth flow handler:
# Opens a browser window for user login and retrieves access tokens
from google_auth_oauthlib.flow import InstalledAppFlow

# Used to refresh expired tokens via HTTP requests
from google.auth.transport.requests import Request

# Handles storing and loading user credentials
from google.oauth2.credentials import Credentials

# Google Calendar API client
from googleapiclient.discovery import build
from googleapiclient.discovery import Resource

import os
import pytz  # Timezone handling library
from typing import List
from datetime import datetime, timedelta, timezone


# Utility Function: Convert English weekday → Arabic
def get_arabic_weekday(dt):
    weekdays = {
        'Monday': 'الاثنين',
        'Tuesday': 'الثلاثاء',
        'Wednesday': 'الأربعاء',
        'Thursday': 'الخميس',
        'Friday': 'الجمعة',
        'Saturday': 'السبت',
        'Sunday': 'الأحد'
    }
    return weekdays.get(dt.strftime('%A'), '')


# Initialize Google Calendar Service
def get_calendar_service(
    SCOPES: List[str],
    CREDENTIALS_FILE: str,
    TOKEN_FILE: str
) -> Resource:
    """
    Creates and returns a Google Calendar API service instance.

    - Loads existing token if available
    - Refreshes token if expired
    - Otherwise starts OAuth login flow
    """

    creds = None

    # Load saved credentials (if exist)
    if os.path.exists(TOKEN_FILE):
        creds = Credentials.from_authorized_user_file(TOKEN_FILE, SCOPES)

    # If credentials are invalid → refresh or re-authenticate
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                CREDENTIALS_FILE,
                SCOPES
            )
            creds = flow.run_local_server(port=0)

        # Save token for future use
        with open(TOKEN_FILE, "w") as token:
            token.write(creds.to_json())

    # Build Google Calendar API client
    service = build("calendar", "v3", credentials=creds)
    return service


# Schedule Appointment
def schedule_appointment(
    SCOPES: List[str],
    CREDENTIALS_FILE: str,
    TOKEN_FILE: str,
    date: str,
    mobile: str,
    tz_name="Asia/Riyadh",
    start_hour=10,
    start_minute=0,
    end_hour=17,
    minutes=30,
) -> str:
    """
    Schedules an appointment for a user if a free time slot exists.

    Logic:
    - Validate date format
    - Ensure date is not in the past
    - Fetch existing events for that day
    - Generate available time slots
    - Book the first free slot
    """

    try:
        # Validate date format
        try:
            base_date = datetime.strptime(date, "%Y-%m-%d")
        except ValueError:
            return "Invalid date format. Use YYYY-MM-DD."

        # Prevent booking in the past
        current_date = datetime.now()
        if base_date < current_date:
            return "Cannot book an appointment in the past."

        tz = pytz.timezone(tz_name)

        # Define start and end of the day
        start_date_time = base_date.replace(hour=0, minute=0, second=0, microsecond=0)
        day_start_local = tz.localize(start_date_time)
        day_end_local = day_start_local + timedelta(days=1)

        # Convert to UTC for API
        day_start = day_start_local.astimezone(pytz.utc).isoformat().replace("+00:00", "Z")
        day_end = day_end_local.astimezone(pytz.utc).isoformat().replace("+00:00", "Z")

        service = get_calendar_service(SCOPES, CREDENTIALS_FILE, TOKEN_FILE)

        # Fetch existing events for the day
        events = service.events().list(
            calendarId='primary',
            timeMin=day_start,
            timeMax=day_end,
            singleEvents=True,
            orderBy='startTime'
        ).execute().get('items', [])

        # Prevent duplicate booking for same user
        if any(mobile in e.get("summary", "") for e in events):
            return f"You already have an appointment on {date}."

        # Collect occupied time slots
        taken_starts = set()
        for e in events:
            s = e.get('start', {})
            dt_local = datetime.fromisoformat(s['dateTime']).astimezone(tz)
            dt_local = dt_local.replace(second=0, microsecond=0)
            taken_starts.add(dt_local)

        # Generate available slots
        slots = int((end_hour - start_hour) * 60 / minutes)
        start_base = tz.localize(base_date.replace(
            hour=start_hour,
            minute=start_minute,
            second=0,
            microsecond=0
        ))

        start_dt = None

        # Find first available slot
        for i in range(slots):
            candidate = (start_base + timedelta(minutes=minutes * i)).replace(second=0, microsecond=0)

            if candidate not in taken_starts:
                start_dt = candidate
                break

        if start_dt is None:
            return f"No available slots on {date}."

        end_dt = start_dt + timedelta(minutes=minutes)

        # Create event
        event = {
            'summary': f'Appointment for {mobile}',
            'start': {'dateTime': start_dt.isoformat(), 'timeZone': tz_name},
            'end': {'dateTime': end_dt.isoformat(), 'timeZone': tz_name},
        }

        service.events().insert(calendarId='primary', body=event).execute()

        weekday_name = get_arabic_weekday(start_dt)

        return (
            f"Appointment booked successfully for {mobile} on "
            f"{weekday_name} ({date}) at {start_dt.strftime('%H:%M')}."
        )

    except Exception as e:
        return f"Failed to schedule appointment: {e}"


# Get User Appointments
def get_appointments(SCOPES, CREDENTIALS_FILE, TOKEN_FILE, mobile: str) -> str:
    """
    Retrieves all upcoming appointments for a specific user.
    """

    try:
        if not mobile:
            return "User identifier (mobile) is required."

        service = get_calendar_service(SCOPES, CREDENTIALS_FILE, TOKEN_FILE)

        now = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")

        events = service.events().list(
            calendarId='primary',
            timeMin=now,
            singleEvents=True,
            orderBy='startTime'
        ).execute().get('items', [])

        user_events = [e for e in events if mobile in e.get("summary", "")]

        if not user_events:
            return "No upcoming appointments found."

        response = "Your upcoming appointments:\n"

        for e in user_events:
            start = e['start'].get('dateTime')
            dt = datetime.fromisoformat(start)

            arabic_day = get_arabic_weekday(dt)

            response += f"- {arabic_day} {dt.strftime('%Y-%m-%d')} at {dt.strftime('%H:%M')}\n"

        return response.strip()

    except Exception as e:
        return f"Failed to retrieve appointments: {e}"


# Cancel Appointment
def cancel_appointment(SCOPES, CREDENTIALS_FILE, TOKEN_FILE, date: str, mobile: str) -> str:
    """
    Cancels a user's appointment for a specific date.
    """

    try:
        if not mobile:
            return "User identifier (mobile) is required."

        try:
            base_date = datetime.strptime(date, "%Y-%m-%d")
        except ValueError:
            return "Invalid date format. Use YYYY-MM-DD."

        service = get_calendar_service(SCOPES, CREDENTIALS_FILE, TOKEN_FILE)

        day_start = datetime.combine(base_date, datetime.min.time()).astimezone(pytz.utc).isoformat().replace("+00:00", "Z")
        day_end = (datetime.combine(base_date, datetime.min.time()) + timedelta(days=1)).astimezone(pytz.utc).isoformat().replace("+00:00", "Z")

        events = service.events().list(
            calendarId='primary',
            timeMin=day_start,
            timeMax=day_end,
            singleEvents=True,
            orderBy='startTime'
        ).execute().get('items', [])

        matching_events = [e for e in events if mobile in e.get("summary", "")]

        if not matching_events:
            return f"No appointment found for {mobile} on {date}."

        event = matching_events[0]

        start_str = event['start'].get('dateTime')
        event_time_obj = datetime.fromisoformat(start_str)

        # Delete event
        service.events().delete(calendarId='primary', eventId=event['id']).execute()

        return f"Appointment on {date} at {event_time_obj.strftime('%H:%M')} has been cancelled."

    except Exception as e:
        return f"Error while cancelling appointment: {e}"