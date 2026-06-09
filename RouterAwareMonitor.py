#!/usr/bin/env python3
"""
Linux Universal System & Network Monitor
----------------------------------------
Architecture: Cross-Filesystem Auditor
Focus: Detecting Local Disks AND Network (Router) Mounts.
"""

import shutil        # For disk space
import os            # For path checking
import subprocess    # For running Linux commands
from datetime import datetime
import json

class RouterAwareMonitor:
    def __init__(self, router_mount_path):
        """
        :param router_mount_path: The local folder where the router USB is mounted.
        """
        self.mount_path = os.path.expanduser(router_mount_path)
        self.report = {
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "local_disks": {},
            "network_disks": {}
        }

    def check_local_disk(self):
        """
        Checks the internal Linux SSD/HDD.
        """
        print(f"[{datetime.now()}] DEBUG: Checking local system disk...")
        try:
            total, used, free = shutil.disk_usage("/")
            self.report["local_disks"]["root"] = {
                "total_gb": round(total / (2**30), 2),
                "used_gb": round(used / (2**30), 2),
                "percent": round((used / total) * 100, 2)
            }
        except Exception as e:
            print(f"ERROR: Local disk check failed: {e}")

    def check_router_disk(self):
        """
        ROOT CAUSE: We check if the mount point exists and if it's 'active'.
        Linux stores all active connections in /proc/mounts.
        """
        print(f"[{datetime.now()}] DEBUG: Looking for Router USB at {self.mount_path}...")
        
        # 1. Check if the folder exists
        if not os.path.exists(self.mount_path):
            self.report["network_disks"]["status"] = "Folder Missing"
            return

        # 2. Check the /proc/mounts file to see if the network is actually connected
        try:
            with open("/proc/mounts", "r") as f:
                mounts = f.read()
                if self.mount_path in mounts:
                    # If it's in /proc/mounts, it's a real network connection!
                    total, used, free = shutil.disk_usage(self.mount_path)
                    self.report["network_disks"] = {
                        "status": "CONNECTED (Online)",
                        "path": self.mount_path,
                        "total_gb": round(total / (2**30), 2),
                        "used_gb": round(used / (2**30), 2),
                        "free_gb": round(free / (2**30), 2)
                    }
                    print(f"[{datetime.now()}] SUCCESS: Router USB found and scanned.")
                else:
                    self.report["network_disks"]["status"] = "DISCONNECTED (Offline)"
                    print(f"[{datetime.now()}] WARNING: Router USB folder exists but is not mounted.")
        except Exception as e:
            print(f"ERROR: Network disk check failed: {e}")

    def run_full_scan(self):
        print("\n" + "="*50)
        print("SYSTEM STORAGE AUDIT")
        print("="*50)
        
        self.check_local_disk()
        self.check_router_disk()
        
        # Output the result as pretty JSON
        print(json.dumps(self.report, indent=4))
        print("="*50 + "\n")

if __name__ == "__main__":
    # Change '~/RouterDrive' to the folder you created in Step 1
    scanner = RouterAwareMonitor(router_mount_path="~/RouterDrive")
    scanner.run_full_scan()