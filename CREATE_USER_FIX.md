# SOLUCIÓN: Crear usuario jdiaz@polifusion.cl en SQL Server

## Problema
El frontend intenta hacer login con `jdiaz@polifusion.cl`, pero en SQL Server solo existe el usuario `jdiaz`.

## Solución Rápida

Ejecutar estos comandos en el Django shell:

```bash
cd "C:\Users\Jesus Diaz\postventa-system\backend"
python manage.py shell
```

Luego ejecutar este código en el shell:

```python
from apps.users.models import User

# Crear usuario jdiaz@polifusion.cl
user = User.objects.create(
    username='jdiaz@polifusion.cl',
    email='jdiaz@polifusion.cl',
    first_name='Jesus',
    last_name='Diaz',
    role='administrador',
    is_active=True,
    is_staff=True,
    is_superuser=True
)
user.set_password('admin123')
user.save()

print(f"Usuario creado: {user.username}")
print(f"Role: {user.role}")
print("Password: admin123")
```

## Resultado
- ✅ Usuario `jdiaz@polifusion.cl` creado
- ✅ Password: `admin123`
- ✅ Role: `administrador`
- ✅ El login ahora funcionará correctamente

## Verificación
Después de crear el usuario, intenta hacer login en la aplicación con:
- Username: `jdiaz@polifusion.cl`
- Password: `admin123`

## Estado del Sistema
- 2 incidencias en SQL Server
- Usuario administrador disponible
- Servidor ejecutándose en http://localhost:8000
