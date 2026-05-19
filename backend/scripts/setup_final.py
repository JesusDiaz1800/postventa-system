import os
import django
import sys
import shutil
from django.core.management import call_command
from django.conf import settings

# Añadir el path del backend para que encuentre los módulos
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'apps.core.settings')
django.setup()

from apps.users.models import User

def purge_storage():
    """
    Scorched Earth Storage: Elimina físicamente documentos de incidencias y reportes obsoletos.
    """
    print("\n" + "="*60)
    print("SCORCHED EARTH STORAGE: ELIMINANDO DOCUMENTOS ANTIGUOS")
    print("="*60)

    # 1. Carpetas en MEDIA_ROOT
    media_docs = os.path.join(settings.MEDIA_ROOT, 'documents')
    
    # Lista de patrones o carpetas a borrar
    targets = [
        'lab_reports', 
        'quality_reports', 
        'supplier_reports',
        'shared_documents' # Carpeta antigua de sync
    ]

    if os.path.exists(media_docs):
        for item in os.listdir(media_docs):
            item_path = os.path.join(media_docs, item)
            # Borrar carpetas de incidencias
            if item.startswith('incident_') or item in targets:
                try:
                    print(f"[*] Eliminando: {item_path}")
                    shutil.rmtree(item_path)
                except Exception as e:
                    print(f"Error eliminando {item_path}: {e}")

    # 2. Carpetas en SHARED_DOCUMENTS_PATH (si existe)
    shared_base = getattr(settings, 'SHARED_DOCUMENTS_PATH', None)
    if shared_base and os.path.exists(shared_base):
        print(f"\n[*] Limpiando Carpeta Compartida: {shared_base}")
        # Recorrer países (CL, PE, CO)
        for country in ['Chile', 'Perú', 'Colombia']:
            country_path = os.path.join(shared_base, country)
            if os.path.exists(country_path):
                for folder in os.listdir(country_path):
                    if folder in ['lab_reports', 'quality_reports', 'supplier_reports', 'incidents']:
                        path_to_del = os.path.join(country_path, folder)
                        try:
                            print(f"[*] Eliminando de Compartida: {path_to_del}")
                            shutil.rmtree(path_to_del)
                        except Exception as e:
                            print(f"Error eliminando {path_to_del}: {e}")

    print("OK: Almacenamiento purgado correctamente.")

def reset_migrations():
    print("\n" + "="*60)
    print("RESETEANDO MIGRACIONES DE APPS LOCALES (SCORCHED EARTH)")
    print("="*60)
    apps_dir = os.path.join(settings.BASE_DIR, 'apps')
    for app in os.listdir(apps_dir):
        app_path = os.path.join(apps_dir, app)
        if os.path.isdir(app_path):
            migrations_dir = os.path.join(app_path, 'migrations')
            # Asegurar que el directorio exista
            if not os.path.exists(migrations_dir):
                os.makedirs(migrations_dir)
            
            # Asegurar que __init__.py exista
            init_file = os.path.join(migrations_dir, '__init__.py')
            if not os.path.exists(init_file):
                open(init_file, 'a').close()
            
            # Borrar las antiguas
            for filename in os.listdir(migrations_dir):
                if filename != '__init__.py' and filename.endswith('.py'):
                    file_path = os.path.join(migrations_dir, filename)
                    os.remove(file_path)
                    print(f"[*] Eliminada migración antigua: {app}/{filename}")
    
    print("\n[+] Generando nuevas migraciones limpias...")
    call_command('makemigrations', interactive=False)
    print("OK: Nuevas migraciones generadas basadas en la arquitectura actual.")

def setup():
    dbs = ['default', 'default_pe', 'default_co']
    
    print("="*60)
    print("SERTEC SYSTEM - CONFIGURACIÓN INICIAL DE BASES DE DATOS")
    print("="*60)

    # 1. Purga de Almacenamiento (Solicitado por el usuario)
    purge_storage()

    # 1.5. Limpiar y recrear migraciones sin dependencias legacy
    reset_migrations()

    # 2. Migraciones
    for db in dbs:
        try:
            print(f"\n[MIGRANDO BASE DE DATOS: {db}]...")
            # Solución para bug nativo de SQL Server con token_blacklist 0008
            try:
                call_command('migrate', 'token_blacklist', '0007_auto_20171017_2214', database=db, interactive=False)
                call_command('migrate', 'token_blacklist', '0008_migrate_to_bigautofield', database=db, fake=True, interactive=False)
                call_command('migrate', 'token_blacklist', database=db, interactive=False)
            except Exception as e:
                print(f"[*] Advertencia token_blacklist: {e} (Continuando con el resto...)")
            
            call_command('migrate', database=db, interactive=False)
            print(f"OK: Migración exitosa en {db}")
        except Exception as e:
            print(f"ERROR: Falló migración en {db}: {e}")

    # 2. Creación de Usuarios
    user_specs = [
        {'username': 'jdiaz', 'email': 'jdiaz@polifusion.cl', 'db': 'default', 'country': 'Chile'},
        {'username': 'jdiaz.pe', 'email': 'jdiaz.pe@polifusion.pe', 'db': 'default_pe', 'country': 'Perú'},
        {'username': 'jdiaz.co', 'email': 'jdiaz.co@polifusion.co', 'db': 'default_co', 'country': 'Colombia'},
    ]

    print("\n" + "="*60)
    print("CREANDO USUARIOS DE ACCESO VIP")
    print("="*60)

    password = 'adminJDR'

    for spec in user_specs:
        db = spec['db']
        username = spec['username']
        country = spec['country']
        
        try:
            if not User.objects.using(db).filter(username=username).exists():
                print(f"[*] Creando superusuario '{username}' para {country} en DB '{db}'...")
                User.objects.db_manager(db).create_superuser(
                    username=username,
                    email=spec['email'],
                    password=password
                )
                print(f"OK: Usuario {username} creado exitosamente.")
            else:
                # Actualizar contraseña si ya existe para asegurar acceso
                user = User.objects.using(db).get(username=username)
                user.set_password(password)
                user.save(using=db)
                print(f"INFO: El usuario '{username}' ya existía. Se actualizó su contraseña.")
        except Exception as e:
            print(f"ERROR: No se pudo crear/actualizar usuario {username} en {db}: {e}")

    print("\n" + "="*60)
    print("¡PROCESO FINALIZADO CON ÉXITO!")
    print("Ahora puedes ingresar al frontend con:")
    print(f" - Usuario: jdiaz, jdiaz.pe o jdiaz.co")
    print(f" - Contraseña: {password}")
    print("="*60)

if __name__ == "__main__":
    setup()
