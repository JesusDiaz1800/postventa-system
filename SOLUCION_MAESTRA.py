import os
import sys
import subprocess
import urllib.request
import time
import re

def kill_port(port):
    print(f"[*] Limpiando puerto {port} y procesos fantasma...")
    try:
        # 1. Matar PM2 de raíz para que no reviva nada
        PM2_PATH = r"C:\Users\jdiaz\AppData\Roaming\npm\pm2.cmd"
        subprocess.run([PM2_PATH, "kill"], shell=True, capture_output=True)
        
        # 2. Matar procesos en el puerto 8000
        result = subprocess.run(['netstat', '-ano'], capture_output=True, text=True)
        lines = result.stdout.split('\n')
        target_pids = set()
        for line in lines:
            if f":{port}" in line and ("LISTENING" in line or "ESTABLISHED" in line):
                parts = re.split(r'\s+', line.strip())
                if len(parts) > 4:
                    pid = parts[-1]
                    target_pids.add(pid)
        for pid in target_pids:
            subprocess.run(['taskkill', '/F', '/PID', pid], capture_output=True)
        
        # 3. Pausa para dejar que Windows libere el puerto
        time.sleep(2)
    except:
        pass

def run():
    # Rutas absolutas
    BASE_DIR = r"C:\Users\jdiaz\Desktop\postventa-system"
    PM2_PATH = r"C:\Users\jdiaz\AppData\Roaming\npm\pm2.cmd"
    CLOUDFLARE_URL = "https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-windows-amd64.exe"
    CLOUDFLARE_EXE = os.path.join(BASE_DIR, "cloudflared.exe")
    
    os.chdir(BASE_DIR)
    
    print("\n" + "="*50)
    print("      SISTEMA POSTVENTA - SOLUCION MAESTRA")
    print("="*50 + "\n")

    # 0. Limpiar puerto
    kill_port(8000)

    # 1. Re-compilar Frontend (Build)
    print("\n[1/4] Re-compilando frontend (esto puede tardar 1 min)...")
    try:
        # Usamos npm run build en la carpeta frontend
        frontend_dir = os.path.join(BASE_DIR, "frontend")
        subprocess.run(["npm.cmd", "run", "build"], cwd=frontend_dir, shell=True, check=True)
        print("      Build exitoso.")
    except Exception as e:
        print(f"      ERROR al compilar: {e}")
        print("      (Asegurate de que Node/NPM esten instalados y funcionando)")
        return

    # 2. Descargar Cloudflare si no existe
    if not os.path.exists(CLOUDFLARE_EXE):
        print("\n[2/4] Descargando herramienta de acceso seguro...")
        try:
            urllib.request.urlretrieve(CLOUDFLARE_URL, CLOUDFLARE_EXE)
            print("      Descarga completada.")
        except Exception as e:
            print(f"      ERROR al descargar: {e}")
            return

    # 2. Reiniciar PM2 para aplicar optimizaciones
    print("[2/3] Reiniciando servicios en modo produccion...")
    try:
        # Usamos shell=True por ser un .cmd en Windows
        subprocess.run([PM2_PATH, "delete", "all"], shell=True, check=False)
        subprocess.run([PM2_PATH, "start", "ecosystem.config.js"], shell=True, check=True)
        subprocess.run([PM2_PATH, "save"], shell=True, check=False)
        print("      Servicios reiniciados correctamente.")
    except Exception as e:
        print(f"      ERROR al reiniciar PM2: {e}")
        print("      (Continuando con el tunel...)")

    # 3. Lanzar Tunel de Cloudflare
    print("[3/3] Lanzando tunel de acceso externo...")
    print("\n" + "-"*50)
    print("ATENCION: Localiza la linea que termina en .trycloudflare.com")
    print("Esa es tu direccion publica gratuita.")
    print("-"*50 + "\n")
    
    # Lanzamos el proceso del tunel
    try:
        subprocess.run([CLOUDFLARE_EXE, "tunnel", "--url", "https://localhost:8000", "--no-tls-verify"], check=True)
    except KeyboardInterrupt:
        print("\nTunel cerrado por el usuario.")
    except Exception as e:
        print(f"ERROR en el tunel: {e}")

if __name__ == "__main__":
    run()
