import smtplib
from email.message import EmailMessage
import os
from dotenv import load_dotenv

# Load env from the backend directory
env_path = os.path.join(os.getcwd(), 'backend', '.env')
load_dotenv(env_path)

SMTP_SERVER = os.getenv('EMAIL_HOST', 'mail.polifusion.cl')
SMTP_PORT = int(os.getenv('EMAIL_PORT', 465))
SMTP_USER = os.getenv('EMAIL_HOST_USER')
SMTP_PASS = os.getenv('EMAIL_HOST_PASSWORD')
USE_TLS = os.getenv('EMAIL_USE_TLS', 'False') == 'True'
USE_SSL = os.getenv('EMAIL_USE_SSL', 'True') == 'True'

print(f"Testing SMTP for {SMTP_USER} on {SMTP_SERVER}:{SMTP_PORT}...")
print(f"Security: SSL={USE_SSL}, TLS={USE_TLS}")

try:
    if USE_SSL:
        print("Using SMTP_SSL (Implicit SSL)...")
        server = smtplib.SMTP_SSL(SMTP_SERVER, SMTP_PORT)
    else:
        print("Using SMTP (Standard)...")
        server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
        if USE_TLS:
            print("Starting TLS...")
            server.starttls()
            
    with server:
        server.set_debuglevel(1)
        print("Attempting login...")
        server.login(SMTP_USER, SMTP_PASS)
        print("\nSUCCESS: SMTP Authentication successful!")
        
        # Optionally send a test email to the user
        msg = EmailMessage()
        msg.set_content("Este es un correo de prueba de Postventa System usando la nueva configuración CPANEL (Puerto 465 SSL).")
        msg['Subject'] = 'PRUEBA Postventa System - CPANEL OK'
        msg['From'] = SMTP_USER
        msg['To'] = 'jdiaz@polifusion.cl'
        
        server.send_message(msg)
        print("Test email sent to jdiaz@polifusion.cl")
except Exception as e:
    print(f"\nFAILED: {str(e)}")
