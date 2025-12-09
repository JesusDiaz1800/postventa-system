#!/usr/bin/env python
"""
Script para instalar WeasyPrint
"""
import subprocess
import sys

def install_weasyprint():
    """Instalar WeasyPrint y dependencias"""
    print("📦 Instalando WeasyPrint...")
    
    try:
        # Instalar WeasyPrint
        subprocess.run([sys.executable, '-m', 'pip', 'install', 'weasyprint'], check=True)
        print("✅ WeasyPrint instalado correctamente")
        
        # En Windows, también instalar GTK
        if sys.platform == 'win32':
            print("📦 Instalando dependencias para Windows...")
            subprocess.run([sys.executable, '-m', 'pip', 'install', 'cffi'], check=True)
            print("✅ Dependencias de Windows instaladas")
        
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Error instalando WeasyPrint: {e}")
        return False

if __name__ == '__main__':
    install_weasyprint()
