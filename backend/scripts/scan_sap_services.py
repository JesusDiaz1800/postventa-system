import socket
import concurrent.futures
import ipaddress

# Subnet to scan
SUBNET = "192.168.1.0/24"
TARGET_PORT = 50000
TIMEOUT = 1.0

# Known interesting IPs
PRIORITY_IPS = ["192.168.1.232", "192.168.1.234"]

def check_port(ip, port):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.settimeout(TIMEOUT)
        result = sock.connect_ex((str(ip), port))
        if result == 0:
            return str(ip)
    return None

def scan_network():
    print(f"Scanning {SUBNET} for port {TARGET_PORT}...")
    
    # Generate all IPs
    network = ipaddress.ip_network(SUBNET)
    all_hosts = list(network.hosts())
    
    # Priority first
    for pip in PRIORITY_IPS:
        print(f"Checking priority IP: {pip}...")
        res = check_port(pip, TARGET_PORT)
        if res:
            print(f"FOUND! Service Layer likely at: {res}:{TARGET_PORT}")
            return res

    print(f"Scanning remaining {len(all_hosts)} hosts (threaded)...")
    
    found_ip = None
    with concurrent.futures.ThreadPoolExecutor(max_workers=50) as executor:
        future_to_ip = {executor.submit(check_port, ip, TARGET_PORT): ip for ip in all_hosts}
        
        for future in concurrent.futures.as_completed(future_to_ip):
            ip = future_to_ip[future]
            try:
                result = future.result()
                if result:
                    print(f"FOUND! Service Layer likely at: {result}:{TARGET_PORT}")
                    found_ip = result
                    # Cancel others? iterating continues but we can break if we only want one
                    # But maybe there are multiple. Let's list all.
            except Exception as e:
                pass
                
    if not found_ip:
        print("Scan complete. No Service Layer found on default port 50000.")
    
    return found_ip

if __name__ == "__main__":
    scan_network()
