import os
import django

# Configuracion de Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'apps.core.settings')
django.setup()

from django.contrib.auth import get_user_model

User = get_user_model()

print("--- Usuarios en la base de datos ---")
for u in User.objects.all():
    print(f"Usuario: {u.username}, Activo: {u.is_active}, Admin: {u.is_superuser}")

# Reset password for jdiaz
jdiaz = User.objects.filter(username='jdiaz').first()
if jdiaz:
    jdiaz.set_password('Admin123456*')
    jdiaz.save()
    print("Se actualizó la contraseña para jdiaz a: Admin123456*")
else:
    print("NO SE ENCONTRO EL USUARIO jdiaz")
