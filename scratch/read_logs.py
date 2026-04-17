import os

log_path = r'backend\logs\postventa.log'
if os.path.exists(log_path):
    with open(log_path, 'r', encoding='utf-8', errors='ignore') as f:
        lines = f.readlines()
        last_lines = lines[-50:]
        print("--- ÚLTIMAS 50 LÍNEAS DE LOG ---")
        for line in last_lines:
            print(line.strip())
else:
    print(f"File not found: {log_path}")
