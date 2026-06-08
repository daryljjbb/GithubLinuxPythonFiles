#!/usr/bin/env python3
"""
Linux System & Network Health Tool
----------------------------------
Architecture: Modular, Class-based
Focus: Error Trapping, Linux Internals, Network Sockets
"""

import os            # Used to check file paths and permissions
import socket        # Used for network connectivity testing
import shutil        # Used for disk usage statistics
import subprocess    # Used to run Linux commands like 'uptime'
import json          # Used to format output (production-ready)
from datetime import datetime

class LinuxMonitor:
    def __init__(self):
        """
        Initialize the monitor. 
        In production, you might load a config file here.
        """
        print(f"[{datetime.now()}] DEBUG: Initializing LinuxMonitor Engine...")
        self.report = {}

    def get_cpu_load(self):
        """
        ROOT CAUSE EXPLANATION:
        On Linux, /proc/loadavg contains the system load averages for the 
        last 1, 5, and 15 minutes. We read this file directly.
        """
        print(f"[{datetime.now()}] DEBUG: Attempting to read /proc/loadavg")
        
        try:
            # We open the virtual file /proc/loadavg
            with open("/proc/loadavg", "r") as f:
                load = f.read().split()
                # load[0] = 1 min, load[1] = 5 min, load[2] = 15 min
                self.report['cpu_load_1min'] = load[0]
                self.report['cpu_load_5min'] = load[1]
                print(f"[{datetime.now()}] SUCCESS: CPU Load captured.")
        except FileNotFoundError:
            # TRAPPING: If this isn't Linux, /proc/loadavg won't exist.
            print(f"[{datetime.now()}] ERROR: /proc/loadavg not found. Is this a Linux system?")
            self.report['cpu_load'] = "N/A"
        except Exception as e:
            # TRAPPING: Catch-all for unexpected permission issues
            print(f"[{datetime.now()}] CRITICAL ERROR: Could not read CPU stats: {e}")
            self.report['cpu_load'] = "Error"

    def get_disk_usage(self, path="/"):
        """
        Checks how much space is left on the Linux filesystem.
        'shutil' is a high-level file operation library.
        """
        print(f"[{datetime.now()}] DEBUG: Checking disk usage for {path}")
        
        try:
            # shutil.disk_usage returns bytes. We convert to GB for readability.
            total, used, free = shutil.disk_usage(path)
            self.report['disk_total_gb'] = round(total / (2**30), 2)
            self.report['disk_used_gb'] = round(used / (2**30), 2)
            self.report['disk_free_gb'] = round(free / (2**30), 2)
            self.report['disk_usage_percent'] = round((used / total) * 100, 2)
            print(f"[{datetime.now()}] SUCCESS: Disk stats calculated.")
        except Exception as e:
            print(f"[{datetime.now()}] ERROR: Failed to access disk path {path}: {e}")
            self.report['disk_error'] = str(e)

    def check_network(self, host="8.8.8.8", port=53, timeout=3):
        """
        Checks network connectivity.
        Instead of 'ping' (which uses ICMP), we use a Socket connection (TCP).
        This is more reliable in production environments.
        """
        print(f"[{datetime.now()}] DEBUG: Testing network connection to {host}:{port}")
        
        try:
            # socket.AF_INET = IPv4
            # socket.SOCK_STREAM = TCP connection
            socket.setdefaulttimeout(timeout)
            socket.socket(socket.AF_INET, socket.SOCK_STREAM).connect((host, port))
            self.report['network_status'] = "Online"
            print(f"[{datetime.now()}] SUCCESS: Internet connection verified.")
        except socket.error as e:
            # TRAPPING: Specifically catch network timeout or refusal
            print(f"[{datetime.now()}] WARNING: Network appears to be OFFLINE: {e}")
            self.report['network_status'] = "Offline"
        except Exception as e:
            print(f"[{datetime.now()}] ERROR: Unexpected network error: {e}")
            self.report['network_status'] = "Unknown Error"

    def get_uptime(self):
        """
        Runs a native Linux command using 'subprocess'.
        This demonstrates how to use Python as a 'wrapper' for Linux CLI tools.
        """
        print(f"[{datetime.now()}] DEBUG: Executing Linux 'uptime' command...")
        
        try:
            # check_output runs the command and captures the text result
            raw_output = subprocess.check_output(["uptime", "-p"]).decode("utf-8")
            self.report['uptime'] = raw_output.strip()
            print(f"[{datetime.now()}] SUCCESS: Uptime retrieved.")
        except subprocess.CalledProcessError as e:
            print(f"[{datetime.now()}] ERROR: Command 'uptime' failed: {e}")
            self.report['uptime'] = "Unknown"
        except Exception as e:
            print(f"[{datetime.now()}] ERROR: General failure running shell commands: {e}")

    def run_all_checks(self):
        """
        Orchestration method to run all modular parts.
        """
        print("\n--- STARTING SYSTEM SCAN ---")
        self.get_cpu_load()
        self.get_disk_usage()
        self.get_uptime()
        self.check_network()
        print("--- SCAN COMPLETE ---\n")

    def display_report(self):
        """
        Prints the final report in a clean, JSON-like format.
        Production tools often output JSON so other programs can read them.
        """
        print("FINAL SYSTEM HEALTH REPORT:")
        # indent=4 makes the output pretty and easy to read
        print(json.dumps(self.report, indent=4))

# --- MAIN EXECUTION BLOCK ---
# This ensures the code only runs if the file is executed directly,
# not if it is imported by another script.
if __name__ == "__main__":
    try:
        # Create an instance of our monitor
        scanner = LinuxMonitor()
        
        # Execute the logic
        scanner.run_all_checks()
        
        # Output the results
        scanner.display_report()

    except KeyboardInterrupt:
        # TRAPPING: Handle the user pressing Ctrl+C gracefully
        print(f"\n[{datetime.now()}] Process interrupted by user. Exiting safely...")
    except Exception as e:
        # TRAPPING: The "Global" error trap for anything we missed
        print(f"FATAL: The script encountered an unhandled error: {e}")