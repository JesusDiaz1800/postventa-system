"""
SSL Certificate Authority & Server Certificate Generator - Postventa System
Genera una Root CA propia para Polifusion y emite certificados firmados.
Esto elimina las alertas de "Conexión No Privada" al instalar la CA en los PCs.
"""
import subprocess
import os
import sys

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

def run_cmd(cmd, description):
    print(f"[SSL] {description}...")
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"[ERROR] {result.stderr}")
        return False
    return True

def generate_ssl():
    # 1. Crear la Root CA (si no existe)
    if not os.path.exists(CA_CERT):
        success = run_cmd([
            'openssl', 'genrsa', '-out', CA_KEY, '4096'
        ], "Generando llave privada de Autoridad Raiz (CA)")
        
        if not success: return False
        
        success = run_cmd([
            'openssl', 'req', '-x509', '-new', '-nodes', '-key', CA_KEY,
            '-sha256', '-days', '3650', '-out', CA_CERT,
            '-subj', '/C=CL/ST=RM/L=Santiago/O=Polifusion/CN=Polifusion-CA'
        ], "Creando Certificado Raiz de Confianza")
        
        if not success: return False
    else:
        print("[INFO] Root CA ya existe. Reutilizando...")

    # 2. Crear llave del Servidor
    run_cmd(['openssl', 'genrsa', '-out', SERVER_KEY, '2048'], "Generando llave del servidor")

    # 3. Crear CSR (Certificate Signing Request) del servidor
    run_cmd([
        'openssl', 'req', '-new', '-key', SERVER_KEY, '-out', SERVER_CSR,
        '-subj', '/C=CL/ST=RM/L=Santiago/O=Polifusion/CN=postventa.local'
    ], "Creando solicitud de firma (CSR)")

    # 4. Crear archivo de extensiones (SAN - Subject Alternative Names)
    # Aqui definimos los nombres por los que se puede acceder
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
    success = run_cmd([
        'openssl', 'x509', '-req', '-in', SERVER_CSR, '-CA', CA_CERT,
        '-CAkey', CA_KEY, '-CAcreateserial', '-out', SERVER_CERT,
        '-days', '825', '-sha256', '-extfile', EXT_FILE
    ], "Firmando certificado con la CA de Polifusion")

    # Limpieza
    if os.path.exists(SERVER_CSR): os.remove(SERVER_CSR)
    if os.path.exists(EXT_FILE): os.remove(EXT_FILE)
    if os.path.exists(os.path.join(SSL_DIR, 'poly-ca-cert.srl')): 
        os.remove(os.path.join(SSL_DIR, 'poly-ca-cert.srl'))

    if success:
        print("\n" + "="*50)
        print("EXITO: Sistema SSL robusto generado")
        print("="*50)
        print(f"1. Certificado Servidor: {SERVER_CERT}")
        print(f"2. Certificado Raiz (CA): {CA_CERT}  <-- ESTE ES EL QUE DEBEN CONFIAR")
        print("="*50)
        return True
    return False

if __name__ == '__main__':
    try:
        if generate_ssl():
            sys.exit(0)
        sys.exit(1)
    except Exception as e:
        print(f"[FATAL] {e}")
        sys.exit(1)
