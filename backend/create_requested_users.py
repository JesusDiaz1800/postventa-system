import os
import sys
import django

# Add backend directory to sys.path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Configure Django settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'apps.core.settings')
django.setup()

from django.contrib.auth import get_user_model

User = get_user_model()

def create_user(username, email, password, first_name, last_name, role, sap_user, sap_password):
    try:
        user = User.objects.filter(username=username).first()
        if not user:
            user = User.objects.create_user(
                username=username,
                email=email,
                password=password,
                first_name=first_name,
                last_name=last_name,
                role=role,
                sap_user=sap_user,
                sap_password=sap_password
            )
            print(f"[OK] Usuario '{username}' creado exitosamente con rol '{role}'.")
        else:
            user.set_password(password)
            user.first_name = first_name
            user.last_name = last_name
            user.role = role
            user.sap_user = sap_user
            user.sap_password = sap_password
            user.save()
            print(f"[OK] Usuario '{username}' actualizado exitosamente.")
    except Exception as e:
        print(f"[ERROR] No se pudo crear/actualizar el usuario '{username}': {e}")

if __name__ == '__main__':
    print("Creando usuarios solicitados...")
    # Jefe de Servicio Técnico
    create_user('pmorales', 'pmorales@polifusion.cl', 'Plf2026**', 'Patricio', 'Morales', 'admin', 'pmorales', 'Plf2026**')
    
    # Técnico
    create_user('tecnico3', 'tecnico3@polifusion.cl', 'pass3456', 'Marco', 'Montenegro', 'technician', 'tecnico3', 'pass3456')
    print("Proceso finalizado.")
