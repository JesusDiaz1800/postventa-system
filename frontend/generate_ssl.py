"""
SSL Certificate Authority & Server Certificate Generator - Postventa System
Genera una Root CA propia para Polifusion y emite certificados firmados.
Esto elimina las alertas de "Conexión No Privada" al instalar la CA en los PCs.
"""
import subprocess
import os
import sys
from datetime import datetime

# Directorios y archivos
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
SSL_DIR = os.path.join(BASE_DIR, 'ssl')
CA_KEY = os.path.join(SSL_DIR, 'poly-ca-key.pem')
CA_CERT = os.path.join(SSL_DIR, 'poly-ca-cert.pem')
SERVER_KEY = os.path.join(SSL_DIR, 'key.pem')
SERVER_CERT = os.path.join(SSL_DIR, 'cert.pem')
SERVER_CSR = os.path.join(SSL_DIR, 'server.csr')
EXT_FILE = os.path.join(SSL_DIR, 'server.ext')

os.makedirs(SSL_DIR, exist_ok=True)

def run_cmd(cmd, description=None):
    if description:
        print(f"[SSL] {description}...")
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        if description:
            print(f"[ERROR] {result.stderr}")
        return False, result.stdout
    return True, result.stdout

def get_cert_expiry():
    if not os.path.exists(SERVER_CERT):
        return None
    
    success, output = run_cmd([
        'openssl', 'x509', '-enddate', '-noout', '-in', SERVER_CERT
    ])
    
    if not success:
        return None
    
    # Formato: notAfter=Feb 12 16:53:18 2027 GMT
    date_str = output.strip().split('=')[1]
    # Remove GMT if present for simpler parsing
    date_str = date_str.replace(' GMT', '')
    try:
        expiry_date = datetime.strptime(date_str, '%b %d %H:%M:%S %Y')
        return expiry_date
    except:
        return None

def generate_ssl(force=False):
    # Verificar si es necesario regenerar
    expiry = get_cert_expiry()
    if not force and expiry:
        days_left = (expiry - datetime.now()).days
        if days_left > 30:
            print(f"[INFO] Certificado valido por {days_left} dias mas. No se requiere renovacion.")
            return True
        print(f"[INFO] Certificado por vencer ({days_left} dias). Renovando automáticamente...")

    # 1. Crear la Root CA (si no existe)
    if not os.path.exists(CA_CERT):
        success, _ = run_cmd([
            'openssl', 'genrsa', '-out', CA_KEY, '4096'
        ], "Generando llave privada de Autoridad Raiz (CA)")
        
        if not success: return False
        
        success, _ = run_cmd([
            'openssl', 'req', '-x509', '-new', '-nodes', '-key', CA_KEY,
            '-sha256', '-days', '3650', '-out', CA_CERT,
            '-subj', '/C=CL/ST=RM/L=Santiago/O=Polifusion/CN=Polifusion-CA'
        ], "Creando Certificado Raiz de Confianza (Validez 10 años)")
        
        if not success: return False
    else:
        print("[INFO] Root CA ya existe. Manteniendo confianza de usuarios...")

    # 2. Crear llave del Servidor
    run_cmd(['openssl', 'genrsa', '-out', SERVER_KEY, '2048'], "Generando llave del servidor")

    # 3. Crear CSR (Certificate Signing Request) del servidor
    run_cmd([
        'openssl', 'req', '-new', '-key', SERVER_KEY, '-out', SERVER_CSR,
        '-subj', '/C=CL/ST=RM/L=Santiago/O=Polifusion/CN=postventa.local'
    ], "Creando solicitud de firma (CSR)")

    # 4. Crear archivo de extensiones (SAN - Subject Alternative Names)
    with open(EXT_FILE, 'w') as f:
        f.write("\n".join([
            "authorityKeyIdentifier=keyid,issuer",
            "basicConstraints=CA:FALSE",
            "keyUsage = digitalSignature, nonRepudiation, keyEncipherment, dataEncipherment",
            "subjectAltName = @alt_names",
            "",
            "[alt_names]",
            "DNS.1 = postventa.local",
            "DNS.2 = localhost",
            "IP.1 = 127.0.0.1",
            "IP.2 = 192.168.1.234",
            "IP.3 = 192.168.1.1"
        ]))

    # 5. Firmar el certificado del servidor con nuestra Root CA
    success, _ = run_cmd([
        'openssl', 'x509', '-req', '-in', SERVER_CSR, '-CA', CA_CERT,
        '-CAkey', CA_KEY, '-CAcreateserial', '-out', SERVER_CERT,
        '-days', '365', '-sha256', '-extfile', EXT_FILE
    ], "Firmando nuevo certificado servidor (Validez 1 año)")

    # Limpieza
    if os.path.exists(SERVER_CSR): os.remove(SERVER_CSR)
    if os.path.exists(EXT_FILE): os.remove(EXT_FILE)
    if os.path.exists(os.path.join(SSL_DIR, 'poly-ca-cert.srl')): 
        os.remove(os.path.join(SSL_DIR, 'poly-ca-cert.srl'))

    if success:
        print("\n" + "="*50)
        print("EXITO: Certificado renovado correctamente")
        print("="*50)
        return True
    return False

if __name__ == '__main__':
    try:
        # Si se pasa el argumento --force, se regenera si o si
        force_regen = '--force' in sys.argv
        if generate_ssl(force=force_regen):
            sys.exit(0)
        sys.exit(1)
    except Exception as e:
        print(f"[FATAL] {e}")
        sys.exit(1)
