#!/usr/bin/env python
"""
Script para instalar Playwright
"""
import subprocess
import sys

def install_playwright():
    """Instalar Playwright y dependencias"""
    print("📦 Instalando Playwright...")
    
    try:
        # Instalar Playwright
        subprocess.run([sys.executable, '-m', 'pip', 'install', 'playwright'], check=True)
        print("✅ Playwright instalado correctamente")
        
        # Instalar navegadores
        subprocess.run([sys.executable, '-m', 'playwright', 'install', 'chromium'], check=True)
        print("✅ Navegador Chromium instalado")
        
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Error instalando Playwright: {e}")
        return False

if __name__ == '__main__':
    install_playwright()
