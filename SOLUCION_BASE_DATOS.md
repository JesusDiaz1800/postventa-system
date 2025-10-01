# SOLUCIÓN: CONECTAR APLICACIÓN A SQL SERVER EXPRESS

## Problema Identificado
- **Base de datos SQLite**: Contiene 1 incidencia
- **Base de datos SQL Server Express**: Contiene 2 incidencias (correcta)
- **Servidor Django**: Está usando SQLite en lugar de SQL Server

## Solución

### Opción 1: Modificar el archivo de configuración predeterminado

Editar `backend/postventa_system/settings.py` y cambiar la configuración de base de datos:

```python
# Reemplazar esta configuración:
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

# Por esta configuración de SQL Server:
DATABASES = {
    'default': {
        'ENGINE': 'mssql',
        'NAME': 'postventa_system',
        'USER': '',  # Empty for Windows Authentication
        'PASSWORD': '',  # Empty for Windows Authentication
        'HOST': 'NB-JDIAZ25\\SQLEXPRESS',
        'PORT': '',
        'OPTIONS': {
            'driver': 'ODBC Driver 17 for SQL Server',
            'extra_params': 'Server=NB-JDIAZ25\\SQLEXPRESS;Database=postventa_system;Trusted_Connection=yes;Encrypt=yes;TrustServerCertificate=yes;',
        },
    }
}
```

### Opción 2: Usar variable de entorno (Recomendado)

Crear un archivo de script para iniciar el servidor con la configuración correcta:

**Archivo: `backend/start_server_sqlserver.ps1`**
```powershell
$env:DJANGO_SETTINGS_MODULE="postventa_system.settings-sqlserver"
python manage.py runserver 8000
```

Ejecutar:
```bash
cd backend
.\start_server_sqlserver.ps1
```

### Opción 3: Modificar manage.py (Más simple)

Editar `backend/manage.py` y cambiar la línea:

```python
# De:
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'postventa_system.settings')

# A:
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'postventa_system.settings-sqlserver')
```

## Verificación

Después de aplicar cualquiera de las opciones anteriores, reiniciar el servidor y verificar:

1. **Detener el servidor actual:**
```bash
taskkill /F /IM python.exe
```

2. **Iniciar el servidor:**
```bash
cd backend
python manage.py runserver 8000
```

3. **Verificar en la aplicación web** que ahora se muestren **2 incidencias**:
   - INC-2025-0001 - Inmobiliaria Los Robles Ltda.
   - INC-2025-0003 - Empresa Constructora Central

## Configuración Permanente (Recomendado)

Para que el sistema siempre use SQL Server, modificar `backend/manage.py`:

```python
#!/usr/bin/env python
"""Django's command-line utility for administrative tasks."""
import os
import sys


def main():
    """Run administrative tasks."""
    # Cambiar esta línea para usar SQL Server por defecto
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'postventa_system.settings-sqlserver')
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc
    execute_from_command_line(sys.argv)


if __name__ == '__main__':
    main()
```

## Estado de las Bases de Datos

### SQLite (`backend/db.sqlite3`)
- Total incidencias: 1
- Usuario: jdiaz@polifusion.cl

### SQL Server Express (`NB-JDIAZ25\SQLEXPRESS`)
- Total incidencias: 2
- Usuario: jdiaz
- Base de datos: postventa_system

## Próximos Pasos

Una vez aplicada la solución, la aplicación web mostrará correctamente las 2 incidencias de SQL Server Express.
