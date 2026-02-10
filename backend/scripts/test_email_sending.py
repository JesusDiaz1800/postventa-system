
import sys
import os
import django

# Setup Django environment
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, BASE_DIR)
print(f"Added to sys.path: {BASE_DIR}")

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'postventa_project.settings')
django.setup()

from apps.incidents.services.email_service import EmailService
from django.conf import settings

print("--- DIAGNOSTICO DE EMAIL ---")
print(f"EMAIL_HOST: {os.getenv('EMAIL_HOST')}")
print(f"EMAIL_PORT: {os.getenv('EMAIL_PORT')}")
print(f"EMAIL_HOST_USER: {os.getenv('EMAIL_HOST_USER')}")
print(f"Has Password? {'Yes' if os.getenv('EMAIL_HOST_PASSWORD') else 'No'}")

print("\nIntentando enviar correo de prueba...")
try:
    success, error = EmailService.send_email_with_attachment(
        subject="Test de Diagnóstico Postventa",
        message="<p>Este es un correo de prueba para verificar la configuración SMTP.</p>",
        recipient_list=["test_recipient@example.com"], # Won't actually matter if auth fails first
    )
    
    if success:
        print("\n[EXITO] El correo se envió (o al menos fue aceptado por el servidor SMTP).")
    else:
        print(f"\n[FALLO] Referencia del Error: {error}")

except Exception as e:
    print(f"\n[CRASH] Excepción no controlada: {e}")
