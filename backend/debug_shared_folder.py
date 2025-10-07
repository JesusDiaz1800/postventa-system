import os
import django
from django.conf import settings

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'postventa_system.settings-sqlserver')
django.setup()

def debug_shared_folder():
    """Verificar qué archivos están disponibles en la carpeta compartida"""
    print("=== DEBUGGING CARPETA COMPARTIDA ===")
    
    # Ruta de la carpeta compartida
    shared_base = getattr(settings, 'SHARED_DOCUMENTS_PATH', None)
    if not shared_base:
        print("❌ SHARED_DOCUMENTS_PATH no configurada")
        return
    
    print(f"📁 Carpeta compartida: {shared_base}")
    print(f"📁 Existe: {os.path.exists(shared_base)}")
    
    if not os.path.exists(shared_base):
        print("❌ La carpeta compartida no existe")
        return
    
    # Verificar estructura de carpetas
    print("\n=== ESTRUCTURA DE CARPETAS ===")
    try:
        for item in os.listdir(shared_base):
            item_path = os.path.join(shared_base, item)
            if os.path.isdir(item_path):
                print(f"📁 {item}/")
                # Verificar subcarpetas
                try:
                    for subitem in os.listdir(item_path):
                        subitem_path = os.path.join(item_path, subitem)
                        if os.path.isdir(subitem_path):
                            print(f"  📁 {subitem}/")
                            # Verificar archivos en incident_86
                            if subitem.startswith('incident_'):
                                try:
                                    files = os.listdir(subitem_path)
                                    if files:
                                        print(f"    📄 Archivos: {files}")
                                    else:
                                        print(f"    📄 (vacía)")
                                except Exception as e:
                                    print(f"    ❌ Error listando archivos: {e}")
                        else:
                            print(f"  📄 {subitem}")
                except Exception as e:
                    print(f"  ❌ Error listando subcarpetas: {e}")
            else:
                print(f"📄 {item}")
    except Exception as e:
        print(f"❌ Error listando carpeta compartida: {e}")
    
    # Buscar específicamente archivos de visit_reports
    print("\n=== BUSCANDO VISIT_REPORTS ===")
    visit_reports_folder = os.path.join(shared_base, 'visit_reports')
    if os.path.exists(visit_reports_folder):
        print(f"📁 visit_reports existe: {visit_reports_folder}")
        try:
            for item in os.listdir(visit_reports_folder):
                item_path = os.path.join(visit_reports_folder, item)
                if os.path.isdir(item_path) and item.startswith('incident_'):
                    print(f"  📁 {item}/")
                    try:
                        files = os.listdir(item_path)
                        if files:
                            print(f"    📄 Archivos: {files}")
                        else:
                            print(f"    📄 (vacía)")
                    except Exception as e:
                        print(f"    ❌ Error: {e}")
        except Exception as e:
            print(f"❌ Error listando visit_reports: {e}")
    else:
        print("❌ visit_reports no existe")
    
    # Buscar archivos con el nombre específico
    print("\n=== BUSCANDO ARCHIVO ESPECÍFICO ===")
    target_filename = "visit_report_RPT-2025-333073.pdf"
    found_files = []
    
    def search_file_recursive(folder, filename):
        """Buscar archivo recursivamente"""
        try:
            for item in os.listdir(folder):
                item_path = os.path.join(folder, item)
                if os.path.isdir(item_path):
                    search_file_recursive(item_path, filename)
                elif filename.lower() in item.lower() or item.lower() in filename.lower():
                    found_files.append(item_path)
        except Exception as e:
            pass
    
    search_file_recursive(shared_base, target_filename)
    
    if found_files:
        print(f"✅ Archivos encontrados:")
        for file_path in found_files:
            print(f"  📄 {file_path}")
    else:
        print(f"❌ Archivo '{target_filename}' no encontrado")
        
        # Buscar archivos similares
        print("\n=== BUSCANDO ARCHIVOS SIMILARES ===")
        similar_files = []
        def find_similar_files(folder):
            try:
                for item in os.listdir(folder):
                    item_path = os.path.join(folder, item)
                    if os.path.isdir(item_path):
                        find_similar_files(item_path)
                    elif 'visit_report' in item.lower() or 'RPT-2025' in item:
                        similar_files.append(item_path)
            except Exception as e:
                pass
        
        find_similar_files(shared_base)
        
        if similar_files:
            print("📄 Archivos similares encontrados:")
            for file_path in similar_files:
                print(f"  📄 {file_path}")
        else:
            print("❌ No se encontraron archivos similares")

if __name__ == "__main__":
    debug_shared_folder()
