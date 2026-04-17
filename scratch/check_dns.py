import socket

def check_dns(domain):
    try:
        print(f"Verificando {domain}...")
        # Obtener IP
        ip = socket.gethostbyname(domain)
        print(f"IP: {ip}")
        
        # En Windows es dificil obtener NS sin librerias extra, 
        # pero podemos intentar ver quien responde por el dominio.
        print("DNS verificado exitosamente.")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    check_dns("polifusion.cl")
    check_dns("www.polifusion.cl")
