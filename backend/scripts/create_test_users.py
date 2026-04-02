import os
import sys
import django

# Setup Django environment
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
os.environ['DJANGO_SETTINGS_MODULE'] = 'apps.core.settings'
django.setup()

from apps.users.models import User
from apps.core.thread_local import set_current_country

def create_users():
    # Establecer contexto de Chile
    set_current_country('CL')
    print("--- Entorno: CHILE ---")

    users_to_create = [
        {
            'username': 'gerlog',
            'email': 'gerlog@polifusion.cl',
            'password': 'Plf2026**',
            'first_name': 'Gerencia',
            'last_name': 'Logistica',
            'role': 'management',
            'sap_user': 'gerlog',
            'sap_password': 'Plf2026**'
        },
        {
            'username': 'gerpro',
            'email': 'gerpro@polifusion.cl',
            'password': 'Plf2026**',
            'first_name': 'Gerencia',
            'last_name': 'Produccion',
            'role': 'management',
            'sap_user': 'gerpro',
            'sap_password': 'Plf2026**'
        }
    ]

    for u_data in users_to_create:
        username = u_data['username']
        if User.objects.filter(username=username).exists():
            print(f"Usuario {username} ya existe. Saltando...")
            continue

        try:
            user = User.objects.create_user(
                username=username,
                email=u_data['email'],
                password=u_data['password'],
                first_name=u_data['first_name'],
                last_name=u_data['last_name'],
                role=u_data['role'],
                sap_user=u_data['sap_user'],
                sap_password=u_data['sap_password']
            )
            print(f"Usuario {username} creado exitosamente con rol {u_data['role']}.")
        except Exception as e:
            print(f"Error al crear usuario {username}: {e}")

if __name__ == "__main__":
    create_users()
