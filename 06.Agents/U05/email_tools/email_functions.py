import smtplib  

from email.message import EmailMessage   
                     
def send_email(to ,subject ,body, settings):
    try:

        msg = EmailMessage()

        msg.set_content(body) 
                 
        msg["Subject"] = subject  

        msg["From"] = settings["from"]    
 
        msg["To"] = to                            
        
        with smtplib.SMTP(settings["server"], settings["port"]) as server:

            server.starttls()      
          
            server.login(settings["from"], settings["password"])  

            server.send_message(msg)            
        
        return f"تم إرسال البريد الإلكتروني إلى : {to}" 
    
    except Exception as e:
        return f"فشل إرسال البريد الإلكتروني: {e}"        
