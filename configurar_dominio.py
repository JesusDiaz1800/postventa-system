import os
import subprocess
import json
import glob
from pathlib import Path

def run_cmd(cmd):
    print(f"> {cmd}")
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"ERROR: {result.stderr}")
    else:
        print(result.stdout)
    return result

def main():
    TUNNEL_NAME = "postventa-tunnel"
    DOMAIN = "incidencias.sistemati.cl"
    LOCAL_URL = "https://localhost:8000"
    
    cf_dir = Path.home() / ".cloudflared"
    cert_path = cf_dir / "cert.pem"
    
    if not cert_path.exists():
        print("ERROR: No se encontró cert.pem. Por favor ejecuta el login de nuevo.")
        return

    print("=== 1. CREANDO TUNEL ===")
    res_create = run_cmd(f"cloudflared.exe tunnel create {TUNNEL_NAME}")
    
    # Extraer ID de la salida (ej: "Created tunnel postventa-tunnel with id 86b09d78...")
    import re
    tunnel_id = None
    output_text = res_create.stdout + " " + res_create.stderr
    match = re.search(r"with id ([a-f0-9\-]+)", output_text)
    if match:
        tunnel_id = match.group(1)
        
    print("=== 2. RUTANDO DNS ===")
    run_cmd(f"cloudflared.exe tunnel route dns {TUNNEL_NAME} {DOMAIN}")
    
    print("=== 3. CONFIGURANDO ROUTING LOCAL ===")
    cred_file = None
    
    # Si no capturó regex, intentar por fuerza bruta los .json
    if not tunnel_id:
        json_files = glob.glob(str(cf_dir / "*.json"))
        for jfile in json_files:
            try:
                with open(jfile, "r") as f:
                    data = json.load(f)
                    # A veces no trae TunnelName, buscar por TunnelID si es el único .json
                    if data.get("TunnelName") == TUNNEL_NAME or len(json_files) == 1:
                        tunnel_id = data.get("TunnelID")
                        cred_file = jfile
                        break
            except Exception:
                pass
    
    if tunnel_id and not cred_file:
        cred_file = str(cf_dir / f"{tunnel_id}.json")
        
    if not tunnel_id:
        print("No se pudo encontrar el TunnelID generado. ¿Seguro que se creó bien?")
        return
        
    print(f"Tunnel ID encontrado: {tunnel_id}")
    
    config_content = f"""tunnel: {tunnel_id}
credentials-file: {cred_file}

ingress:
  - hostname: {DOMAIN}
    service: {LOCAL_URL}
    originRequest:
      noTLSVerify: true
  - service: http_status:404
"""
    
    config_path = cf_dir / "config.yml"
    with open(config_path, "w") as f:
        f.write(config_content)
    
    print(f"Archivo de configuracion creado exitosamente en: {config_path}")
    
    print("=== TODO LISTO ===")
    print("Nota: El tunel no se instaló como servicio porque lo manejaremos con PM2.")
    print(f"Ahora puedes visitar tu dominio: {DOMAIN}")

if __name__ == "__main__":
    main()
