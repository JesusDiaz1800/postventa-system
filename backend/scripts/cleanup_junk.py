import os
import shutil
import glob

def cleanup_project():
    """
    Script de limpieza profesional para el Sistema Postventa.
    Elimina archivos temporales, logs y scripts de depuración.
    """
    print("🧹 Iniciando limpieza de mantenimiento...")
    
    # Directorios base
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    backend_dir = os.path.join(base_dir, "backend")
    
    # Patrones de archivos basura (Junk)
    junk_patterns = [
        "check_*.py", "debug_*.py", "test_*.py", "verify_*.py", 
        "tmp_*.py", "inspect_*.py", "find_*.py", "list_*.py",
        "*.log", "*.txt.bak", "gemini_*.txt", "models_list.txt"
    ]
    
    deleted_count = 0
    
    # 1. Limpieza en la raíz del backend
    for pattern in junk_patterns:
        files = glob.glob(os.path.join(backend_dir, pattern))
        for f in files:
            try:
                os.remove(f)
                print(f"🗑️ Eliminado: {os.path.basename(f)}")
                deleted_count += 1
            except Exception as e:
                print(f"❌ Error eliminando {f}: {e}")
                
    # 2. Limpieza de __pycache__ recursiva
    for root, dirs, files in os.walk(backend_dir):
        if "__pycache__" in dirs:
            pycache_path = os.path.join(root, "__pycache__")
            try:
                shutil.rmtree(pycache_path)
                print(f"📁 Limpiado: {os.path.relpath(pycache_path, backend_dir)}")
            except Exception as e:
                print(f"❌ Error eliminando pycache en {root}: {e}")

    print(f"\n✨ Limpieza completada. Archivos eliminados: {deleted_count}")

if __name__ == "__main__":
    cleanup_project()
