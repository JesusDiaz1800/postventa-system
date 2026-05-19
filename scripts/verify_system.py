"""
Script para verificar el sistema antes del despliegue
"""
import os
import sys
import django
from django.core.management import execute_from_command_line
from django.db import connections
from django.conf import settings

def check_database():
    """Verificar conexión a la base de datos"""
    try:
        with connections['default'].cursor() as cursor:
            cursor.execute("SELECT 1")
            cursor.fetchone()
            print("✅ Conexión a la base de datos OK")
            return True
    except Exception as e:
        print(f"❌ Error en la base de datos: {e}")
        return False

def check_media_paths():
    """Verificar rutas de medios y permisos"""
    paths_to_check = [
        settings.MEDIA_ROOT,
        settings.STATIC_ROOT,
        os.path.join(settings.BASE_DIR, 'logs')
    ]
    
    all_ok = True
    for path in paths_to_check:
        if not os.path.exists(path):
            try:
                os.makedirs(path)
                print(f"✅ Creado directorio: {path}")
            except Exception as e:
                print(f"❌ No se pudo crear {path}: {e}")
                all_ok = False
        
        # Verificar permisos
        try:
            test_file = os.path.join(path, 'test.txt')
            with open(test_file, 'w') as f:
                f.write('test')
            os.remove(test_file)
            print(f"✅ Permisos OK en {path}")
        except Exception as e:
            print(f"❌ Error de permisos en {path}: {e}")
            all_ok = False
    
    return all_ok

def check_redis():
    """Verificar conexión a Redis"""
    try:
        from django_redis import get_redis_connection
        conn = get_redis_connection("default")
        conn.ping()
        print("✅ Conexión a Redis OK")
        return True
    except Exception as e:
        print(f"❌ Error en Redis: {e}")
        return False

def check_environment_variables():
    """Verificar variables de entorno requeridas"""
    required_vars = [
        'DJANGO_SECRET_KEY',
        'DB_PASSWORD',
        'REDIS_URL'
    ]
    
    all_ok = True
    for var in required_vars:
        if not os.environ.get(var):
            print(f"❌ Falta variable de entorno: {var}")
            all_ok = False
        else:
            print(f"✅ Variable {var} configurada")
    
    return all_ok

def check_installed_apps():
    """Verificar aplicaciones instaladas"""
    required_apps = [
        'apps.incidents',
        'apps.documents',
        'apps.users',
        'apps.audit',
        'apps.workflows'
    ]
    
    all_ok = True
    for app in required_apps:
        if app not in settings.INSTALLED_APPS:
            print(f"❌ Falta aplicación: {app}")
            all_ok = False
        else:
            print(f"✅ Aplicación {app} instalada")
    
    return all_ok

def main():
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'postventa_system.settings-production')
    django.setup()
    
    print("\n=== Verificación del Sistema ===\n")
    
    checks = [
        ("Base de datos", check_database),
        ("Rutas y permisos", check_media_paths),
        ("Redis", check_redis),
        ("Variables de entorno", check_environment_variables),
        ("Aplicaciones", check_installed_apps)
    ]
    
    all_passed = True
    for name, check_func in checks:
        print(f"\nVerificando {name}...")
        if not check_func():
            all_passed = False
    
    if all_passed:
        print("\n✅ Todas las verificaciones pasaron exitosamente")
        sys.exit(0)
    else:
        print("\n❌ Algunas verificaciones fallaron")
        sys.exit(1)

if __name__ == '__main__':
    main()