#!/usr/bin/env python
"""
Script completo para iniciar el servidor con SQL Server
"""
import os
import sys
import subprocess
import time

def start_server():
    """Iniciar servidor Django con SQL Server"""
    print("=" * 60)
    print("    INICIANDO SERVIDOR CON SQL SERVER EXPRESS")
    print("=" * 60)
    
    # Configurar variable de entorno
    os.environ['DJANGO_SETTINGS_MODULE'] = 'postventa_system.settings-sqlserver'
    
    print("✅ Configuración: SQL Server Express")
    print("✅ Base de datos: postventa_system")
    print("✅ Servidor: NB-JDIAZ25\\SQLEXPRESS")
    print()
    
    try:
        # Verificar que estamos en el directorio correcto
        if not os.path.exists('manage.py'):
            print("❌ Error: No se encuentra manage.py")
            print("   Asegúrate de ejecutar desde el directorio backend/")
            return False
        
        print("✅ Archivo manage.py encontrado")
        print("✅ Iniciando servidor Django...")
        print()
        print("🌐 Servidor disponible en: http://localhost:8000")
        print("📊 API disponible en: http://localhost:8000/api/")
        print("🔍 Incidencias: http://localhost:8000/api/incidents/")
        print()
        print("Presiona Ctrl+C para detener el servidor")
        print("=" * 60)
        
        # Iniciar servidor
        subprocess.run([sys.executable, 'manage.py', 'runserver', '8000'])
        
    except KeyboardInterrupt:
        print("\n\n🛑 Servidor detenido por el usuario")
    except Exception as e:
        print(f"\n❌ Error iniciando servidor: {e}")
        return False
    
    return True

if __name__ == "__main__":
    start_server()
