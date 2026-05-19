import socket
import os
import sys
import threading
from queue import Queue

def get_local_ip():
    """Detecta la IP local de la maquina en la red"""
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except Exception:
        return "127.0.0.1"

def check_port(ip, port=1433, timeout=0.5):
    """Verifica si el puerto esta abierto"""
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(timeout)
        result = s.connect_ex((ip, port))
        s.close()
        return result == 0
    except:
        return False

def scan_network_for_sql(base_ip_range):
    """Escanea la red buscando SQL Server (puerto 1433)"""
    print(f"Buscando SQL Server en la red {base_ip_range}.x ...")
    found_ips = []
    
    def worker():
        while True:
            ip_end = q.get()
            if ip_end is None:
                break
            ip = f"{base_ip_range}.{ip_end}"
            if check_port(ip, 1433, timeout=0.2):
                found_ips.append(ip)
                print(f" ENCONTRADO! SQL Server en {ip}")
            q.task_done()

    q = Queue()
    threads = []
    
    # Lanzar 50 hilos para escanear rapido
    for _ in range(50):
        t = threading.Thread(target=worker)
        t.daemon = True
        t.start()
        threads.append(t)
        
    # Escanear rango 1-254
    for i in range(1, 255):
        q.put(i)
        
    q.join()
    
    # Detener hilos
    for _ in range(50):
        q.put(None)
        
    for t in threads:
        t.join()
        
    return found_ips

def update_env_file(ip):
    """Actualiza la variable DB_HOST en el archivo .env"""
    current_dir = os.path.dirname(os.path.abspath(__file__))
    backend_dir = os.path.dirname(current_dir)
    env_path = os.path.join(backend_dir, '.env')
    
    if not os.path.exists(env_path):
        print(f"No se encontro el archivo .env en {env_path}")
        return False

    try:
        with open(env_path, 'r') as f:
            lines = f.readlines()
        
        new_lines = []
        updated = False
        current_host = ""
        
        for line in lines:
            if line.strip().startswith('DB_HOST='):
                current_host = line.split('=')[1].strip()
                if current_host == ip:
                    print(f"La configuracion ya es correcta (DB_HOST={ip})")
                    return True
                
                print(f"Actualizando DB_HOST de {current_host} a {ip}...")
                new_lines.append(f'DB_HOST={ip}\n')
                updated = True
            else:
                new_lines.append(line)
        
        if not updated:
            print(f"Agregando DB_HOST={ip} al archivo .env")
            new_lines.append(f'\nDB_HOST={ip}\n')
            
        with open(env_path, 'w') as f:
            f.writelines(new_lines)
            
        print(f"Archivo .env actualizado exitosamente.")
        return True
    
    except Exception as e:
        print(f"Error actualizando .env: {e}")
        return False

def main():
    print("===============================================")
    print("   DETECTOR AUTOMATICO DE SQL SERVER")
    print("===============================================")
    
    local_ip = get_local_ip()
    print(f"Tu IP Local: {local_ip}")
    base_ip = '.'.join(local_ip.split('.')[:-1])
    
    # 1. Primero verificar si la IP actual configurada funciona
    # Esto ahorra tiempo si la IP no ha cambiado
    current_dir = os.path.dirname(os.path.abspath(__file__))
    backend_dir = os.path.dirname(current_dir)
    env_path = os.path.join(backend_dir, '.env')
    current_configured_ip = None
    if os.path.exists(env_path):
        with open(env_path, 'r') as f:
            for line in f:
                if line.strip().startswith('DB_HOST='):
                    current_configured_ip = line.split('=')[1].strip()
                    break
    
    if current_configured_ip and check_port(current_configured_ip, 1433):
        print(f"Conexion exitosa con IP configurada actual: {current_configured_ip}")
        print("No se requieren cambios.")
        print("===============================================\n")
        return

    # 2. Si no funciona, escanear la red
    print(f"La IP configurada no responde o no existe. Escaneando red {base_ip}.0/24...")
    found_ips = scan_network_for_sql(base_ip)
    
    target_ip = None
    
    if len(found_ips) == 0:
        print("No se encontraron servidores SQL en la red.")
        print("Intentando localhost...")
        if check_port('127.0.0.1', 1433):
            target_ip = '127.0.0.1'
            print("Encontrado en localhost.")
    elif len(found_ips) == 1:
        target_ip = found_ips[0]
        print(f"Servidor unico encontrado: {target_ip}")
    else:
        print(f"Multiples servidores encontrados: {found_ips}")
        # Preferir la IP local si esta en la lista, sino la primera encontrada
        if local_ip in found_ips:
            target_ip = local_ip
        else:
            target_ip = found_ips[0]
        print(f"Seleccionando: {target_ip}")

    # 3. Actualizar configuracion
    if target_ip:
        update_env_file(target_ip)
    else:
        print("ADVERTENCIA: No se pudo determinar la IP del servidor de base de datos.")
    
    print("===============================================\n")

if __name__ == "__main__":
    main()
