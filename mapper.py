#!/usr/bin/env python3
"""
Linux Network & Process Mapper
------------------------------
Architecture: Modular, High-Performance
Focus: Sockets, /proc filesystem exploration, Exception Handling
"""

import socket        # For network port scanning
import os            # For navigating the Linux /proc filesystem
import datetime      # For timestamping logs
import json          # For structured data output

class NetworkProcessMapper:
    def __init__(self):
        print(f"[{datetime.datetime.now()}] DEBUG: Initializing Mapper Engine...")
        self.results = {
            "open_ports": [],
            "running_processes": [],
            "scan_info": {}
        }

    def scan_common_ports(self):
        """
        ROOT CAUSE: Services (like VS Code, Web Servers, SSH) "listen" on Ports.
        We try to create a connection to see if anyone is 'home'.
        """
        # Common ports: 22 (SSH), 80 (HTTP), 443 (HTTPS), 5432 (Postgres), 8080 (Dev)
        target_ports = [22, 80, 443, 3000, 5432, 8000, 8080]
        target_host = "127.0.0.1" # 'localhost' - your own machine
        
        print(f"[{datetime.datetime.now()}] DEBUG: Scanning common ports on {target_host}...")

        for port in target_ports:
            # We use a context manager ('with') to ensure the socket closes automatically
            # AF_INET = IPv4, SOCK_STREAM = TCP
            try:
                with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                    s.settimeout(0.5) # Don't wait more than half a second per port
                    # .connect_ex returns 0 if the port is OPEN
                    result = s.connect_ex((target_host, port))
                    
                    if result == 0:
                        print(f"[{datetime.datetime.now()}] SUCCESS: Found OPEN port: {port}")
                        self.results["open_ports"].append(port)
                    else:
                        # Port is closed or filtered
                        pass 
            except Exception as e:
                print(f"[{datetime.datetime.now()}] ERROR: Failed scanning port {port}: {e}")

    def map_running_processes(self):
        """
        ROOT CAUSE: On Linux, the /proc directory contains a folder for every 
        running process. The folder name is the Process ID (PID).
        Inside each folder, a file named 'comm' contains the name of the program.
        """
        print(f"[{datetime.datetime.now()}] DEBUG: Mapping /proc filesystem...")
        process_count = 0
        
        try:
            # List all items in /proc
            for pid in os.listdir('/proc'):
                # We only care about folders that are numeric (the PIDs)
                if pid.isdigit():
                    try:
                        # Path to the 'command' name file
                        comm_path = os.path.join('/proc', pid, 'comm')
                        
                        with open(comm_path, 'r') as f:
                            process_name = f.read().strip()
                            
                        # We only grab the first 10 for this demo to keep output clean
                        if process_count < 10:
                            self.results["running_processes"].append({
                                "pid": pid,
                                "name": process_name
                            })
                        process_count += 1
                        
                    except (PermissionError, FileNotFoundError):
                        # ROOT CAUSE: Some processes are owned by 'root' or 'kernel'.
                        # Our script (running as your user) isn't allowed to see them.
                        # We "trap" this so the script doesn't crash.
                        continue 
            
            self.results["scan_info"]["total_processes_detected"] = process_count
            print(f"[{datetime.datetime.now()}] SUCCESS: Mapped {process_count} processes.")
            
        except Exception as e:
            print(f"[{datetime.datetime.now()}] CRITICAL: Could not access /proc: {e}")

    def run_discovery(self):
        """
        Orchestration logic.
        """
        print("\n" + "="*50)
        print("SYSTEM DISCOVERY STARTING")
        print("="*50)
        
        self.scan_common_ports()
        self.map_running_processes()
        
        print("="*50)
        print("DISCOVERY COMPLETE\n")

    def display_results(self):
        """
        Print findings in a beautiful production-ready format.
        """
        print(json.dumps(self.results, indent=4))

# --- ENTRY POINT ---
if __name__ == "__main__":
    # Create the scanner object
    mapper = NetworkProcessMapper()
    
    try:
        mapper.run_discovery()
        mapper.display_results()
    except KeyboardInterrupt:
        print("\nShutdown requested by user...")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")