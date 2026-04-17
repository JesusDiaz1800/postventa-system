import subprocess
import os
import re

def kill_port(port):
    print(f"Buscando procesos en el puerto {port}...")
    try:
        # Encontrar el PID
        result = subprocess.run(['netstat', '-ano'], capture_output=True, text=True)
        lines = result.stdout.split('\n')
        target_pids = set()
        for line in lines:
            if f":{port}" in line and "LISTENING" in line:
                parts = re.split(r'\s+', line.strip())
                if len(parts) > 4:
                    pid = parts[-1]
                    target_pids.add(pid)
        
        if not target_pids:
            print(f"No se encontraron procesos en el puerto {port}.")
            return

        for pid in target_pids:
            print(f"Matando proceso con PID: {pid}...")
            subprocess.run(['taskkill', '/F', '/PID', pid], check=False)
        print("Puerto liberado.")
    except Exception as e:
        print(f"Error liberando puerto: {e}")

if __name__ == "__main__":
    kill_port(8000)
    # También limpiar PM2
    try:
        pm2_path = r"C:\Users\jdiaz\AppData\Roaming\npm\pm2.cmd"
        subprocess.run([pm2_path, "delete", "all"], check=False)
        print("PM2 limpiado.")
    except:
        pass
