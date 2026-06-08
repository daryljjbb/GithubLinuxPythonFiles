#!/usr/bin/env python3
"""
Linux Service Installer
-----------------------
Architecture: System Administration Scripting
Focus: Deploying Systemd units and managing background processes.
"""

import os
import subprocess
import sys
from datetime import datetime

SERVICE_NAME = "python-media.service"
# The standard Linux directory for system services
SYSTEMD_PATH = f"/etc/systemd/system/{SERVICE_NAME}"

class ServiceInstaller:
    def __init__(self):
        self.user = os.getlogin()
        self.script_path = os.path.abspath("media_server.py")
        self.work_dir = os.path.dirname(self.script_path)

    def create_service_file(self):
        """
        Generates the Systemd configuration string.
        """
        content = f"""[Unit]
Description=My Python Media Server
After=network.target

[Service]
User={self.user}
WorkingDirectory={self.work_dir}
ExecStart=/usr/bin/python3 {self.script_path}
Restart=always

[Install]
WantedBy=multi-user.target
"""
        return content

    def install(self):
        print(f"[{datetime.now()}] DEBUG: Installing service as {self.user}...")
        
        # ROOT CAUSE: /etc/systemd/system is protected. Sudo is required.
        if os.getuid() != 0:
            print("[!] ERROR: Must run with 'sudo' to install services.")
            return

        # 1. Write the file to the system directory
        try:
            with open(SYSTEMD_PATH, 'w') as f:
                f.write(self.create_service_file())
            print(f"[+] Service file created at {SYSTEMD_PATH}")
        except Exception as e:
            print(f"[-] Failed to write service file: {e}")
            return

        # 2. Tell Linux to find the new service
        subprocess.run(["systemctl", "daemon-reload"])
        
        # 3. Enable it (start on boot)
        subprocess.run(["systemctl", "enable", SERVICE_NAME])
        
        # 4. Start it now
        subprocess.run(["systemctl", "start", SERVICE_NAME])
        
        print("\n" + "="*50)
        print("SUCCESS: Your Media Server is now a BACKGROUND SERVICE!")
        print(f"Command to check status: systemctl status {SERVICE_NAME}")
        print(f"Command to stop:         sudo systemctl stop {SERVICE_NAME}")
        print("="*50)

if __name__ == "__main__":
    installer = ServiceInstaller()
    installer.install()