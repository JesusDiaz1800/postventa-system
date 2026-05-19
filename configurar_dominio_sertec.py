import os
import subprocess
import json
import glob
import re
from pathlib import Path

def run_cmd(cmd):
    print(f"> {cmd}")
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    if result.returncode != 0:
        # A veces el error es solo que ya existe, lo cual esta bien
        if "already exists" in result.stderr:
             print("INFO: El tunel o ruta ya existe, continuando...")
        else:
             print(f"DEBUG: {result.stderr}")
    else:
        print(result.stdout)
    return result

def main():
    # DATOS MAESTROS DE SERTEC
    TUNNEL_NAME = "sertec-tunnel"
    TUNNEL_ID = "a3a92e55-28dd-48a5-8165-d3775514d388"
    DOMAIN = "sertec.polifusion.com"
    LOCAL_URL = "http://localhost:8001"
    
    cf_dir = Path.home() / ".cloudflared"
    cert_path = cf_dir / "cert.pem"
    
    if not cert_path.exists():
        print("ERROR: No se encontro cert.pem. Por favor ejecuta: cloudflared.exe tunnel login")
        return

    print(f"=== 1. VERIFICANDO TUNEL SERTEC ({TUNNEL_NAME}) ===")
    run_cmd(f"cloudflared.exe tunnel create {TUNNEL_NAME}")
    
    print(f"=== 2. RUTANDO DNS A {DOMAIN} ===")
    # Forzamos el ruteo para asegurar que apunte al ID correcto
    run_cmd(f"cloudflared.exe tunnel route dns -f {TUNNEL_ID} {DOMAIN}")
    
    print(f"=== 3. CONFIGURANDO ROUTING LOCAL (DAPHNE 8001) ===")
    
    # El archivo de credenciales DEBE llamarse [TUNNEL_ID].json
    cred_file = cf_dir / f"{TUNNEL_ID}.json"
    
    if not cred_file.exists():
        print(f"ADVERTENCIA: No se encontro {cred_file}. Buscando archivos JSON alternativos...")
        json_files = glob.glob(str(cf_dir / "*.json"))
        if json_files:
            cred_file = Path(json_files[0])
            print(f"Usando archivo encontrado: {cred_file}")
        else:
            print("ERROR CRITICO: No se encontraron credenciales JSON.")
            return
        
    print(f"Tunnel ID Vinculado: {TUNNEL_ID}")
    print(f"Archivo de Credenciales: {cred_file}")
    
    config_content = f"""tunnel: {TUNNEL_ID}
credentials-file: {cred_file}

ingress:
  - hostname: {DOMAIN}
    service: {LOCAL_URL}
  - service: http_status:404
"""
    
    # Escribir en la carpeta oficial de cloudflared
    config_path = cf_dir / "config.yml"
    with open(config_path, "w") as f:
        f.write(config_content)
    
    # Backup en la raiz del proyecto
    with open("cloudflared_config.yml", "w") as f:
        f.write(config_content)
    
    print(f"Archivo de configuracion REPARADO exitosamente en: {config_path}")
    print("=== PROCESO COMPLETADO EXITOSAMENTE ===")

if __name__ == "__main__":
    main()
