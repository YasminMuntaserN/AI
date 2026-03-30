import email_functions as em
import os
from dotenv import load_dotenv

load_dotenv()

print(os.getenv("EMAIL_PASSWORD"))

smtp_settings = {

        "from": os.getenv("EMAIL_FROM", "yasminmun13@gmail.com"),  
        "password": os.getenv("EMAIL_PASSWORD", "fujrvupxwdidfnxs"),
        "server": os.getenv("SMTP_SERVER", "smtp.gmail.com"),
        "port": int(os.getenv("SMTP_PORT", 587))
    }

msg = em.send_email(

    to = "yasminmun13@gmail.com",        
    subject = "اختبار",                
    body = f"هذا اختبار إرسال بريد الكتروني من بايثون",
    settings=smtp_settings                           
)

print(msg)


