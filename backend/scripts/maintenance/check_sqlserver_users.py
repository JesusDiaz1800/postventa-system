import os
import sys
import django

# Configurar Django para usar SQL Server
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'postventa_system.settings-sqlserver')
django.setup()

from apps.users.models import User

def check_sqlserver_users():
    """Verificar usuarios en SQL Server"""
    print("=== VERIFICANDO USUARIOS EN SQL SERVER ===")
    
    try:
        # Obtener todos los usuarios
        users = User.objects.all()
        print(f"Total usuarios en SQL Server: {users.count()}")
        
        for user in users:
            print(f"  - ID: {user.id}, Username: {user.username}, Email: {user.email}, Role: {user.role}")
        
        # Buscar usuario específico
        try:
            user = User.objects.get(username='jdiaz@polifusion.cl')
            print(f"\nUsuario encontrado: {user.username} (ID: {user.id})")
        except User.DoesNotExist:
            print("\nUsuario 'jdiaz@polifusion.cl' no encontrado en SQL Server")
            
            # Buscar usuarios similares
            similar_users = User.objects.filter(username__icontains='jdiaz')
            if similar_users.exists():
                print("Usuarios similares encontrados:")
                for user in similar_users:
                    print(f"  - {user.username}")
            else:
                print("No se encontraron usuarios similares")
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    check_sqlserver_users()
