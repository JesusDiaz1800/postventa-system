from smtplib import SMTP
import sys

try:
    print("Conectando a smtp.office365.com:587...")
    with SMTP('smtp.office365.com', 587, timeout=10) as smtp:
        # smtp.set_debuglevel(1)
        smtp.starttls()
        smtp.login('sapbopolifusion@polifusion.cl', 'Sb_Plfsn_3875002')
        print("¡Inició sesión correctamente en Office365 SMTP!")
except Exception as e:
    print(f"Error SMTP: {str(e)}")
    sys.exit(1)
