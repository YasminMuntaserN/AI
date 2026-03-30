import calendar_functions as cal

SCOPES = ["https://www.googleapis.com/auth/calendar"]  

CREDENTIALS_FILE = "credentials.json"   
          
TOKEN_FILE = "token.json"

mobile1 = "1111"

mobile2 = "2222"

tz_name = "Asia/Riyadh"

d = "2026-04-25"
d2= "2026-04-26"

if __name__ == "__main__":

    print(cal.schedule_appointment(SCOPES, CREDENTIALS_FILE, TOKEN_FILE, d, mobile1, tz_name))

    print(cal.schedule_appointment(SCOPES, CREDENTIALS_FILE, TOKEN_FILE, d, mobile2, tz_name))


    print(cal.get_appointments(SCOPES, CREDENTIALS_FILE, TOKEN_FILE, mobile2))

    print(cal.cancel_appointment(SCOPES, CREDENTIALS_FILE, TOKEN_FILE, d, mobile2))

    print(cal.get_appointments(SCOPES, CREDENTIALS_FILE, TOKEN_FILE, mobile2))