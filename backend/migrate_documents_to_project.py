import os
import shutil
import django
from django.conf import settings

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'postventa_system.settings-sqlserver')
django.setup()

def migrate_documents_to_project():
    """
    Migrar documentos desde la carpeta compartida al proyecto
    """
    print("=== MIGRANDO DOCUMENTOS AL PROYECTO ===")
    
    # Rutas
    old_shared_path = r"Y:\CONTROL DE CALIDAD\postventa"
    new_documents_path = getattr(settings, 'DOCUMENTS_PATH', os.path.join(settings.BASE_DIR, 'documents'))
    
    print(f"Carpeta origen: {old_shared_path}")
    print(f"Carpeta destino: {new_documents_path}")
    
    if not os.path.exists(old_shared_path):
        print("La carpeta compartida no existe. Saltando migracion.")
        return
    
    # Crear estructura de carpetas en el proyecto
    folders_to_migrate = [
        'visit_reports',
        'lab_reports', 
        'supplier_reports',
        'quality_reports',
        'incident_attachments'
    ]
    
    migrated_count = 0
    
    for folder in folders_to_migrate:
        old_folder = os.path.join(old_shared_path, folder)
        new_folder = os.path.join(new_documents_path, folder)
        
        if os.path.exists(old_folder):
            print(f"\nMigrando {folder}...")
            
            # Crear carpeta destino si no existe
            os.makedirs(new_folder, exist_ok=True)
            
            try:
                # Copiar todo el contenido
                for item in os.listdir(old_folder):
                    old_item_path = os.path.join(old_folder, item)
                    new_item_path = os.path.join(new_folder, item)
                    
                    if os.path.isdir(old_item_path):
                        if os.path.exists(new_item_path):
                            shutil.rmtree(new_item_path)
                        shutil.copytree(old_item_path, new_item_path)
                        print(f"  Carpeta copiada: {item}")
                    else:
                        shutil.copy2(old_item_path, new_item_path)
                        print(f"  Archivo copiado: {item}")
                        migrated_count += 1
                        
            except Exception as e:
                print(f"  Error copiando {folder}: {e}")
        else:
            print(f"  Carpeta {folder} no existe en origen")
    
    print(f"\nMigracion completada. {migrated_count} archivos migrados.")
    print(f"Documentos ahora estan en: {new_documents_path}")

if __name__ == "__main__":
    migrate_documents_to_project()
