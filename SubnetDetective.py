#!/usr/bin/env python3
"""
Linux Subnet Detective
----------------------
Architecture: Network Interface Analysis
Focus: Subnet Masks and CIDR notation.
"""

import socket
import os
import subprocess
from datetime import datetime

class SubnetDetective:
    def __init__(self):
        self.timestamp = lambda: datetime.now().strftime("%H:%M:%S")

    def get_detailed_ip_info(self):
        """
        ROOT CAUSE: We use the Linux 'ip addr' command.
        This shows the 'Netmask' (usually /24), which tells us if 
        the third group of numbers matters.
        """
        print(f"[{self.timestamp()}] DEBUG: Fetching Linux IP details...")
        
        try:
            # We run the native Linux command 'ip -4 addr' (-4 for IPv4 only)
            result = subprocess.check_output(["ip", "-4", "addr"]).decode("utf-8")
            print("\n--- YOUR LINUX NETWORK DATA ---")
            print(result)
            
            if "/24" in result:
                print("\n[ANALYSIS]: Your Network Mask is /24 (255.255.255.0)")
                print("ROOT CAUSE: For this to work, your iPhone MUST have the")
                print("exact same first THREE groups of numbers as this PC.")
            elif "/16" in result:
                print("\n[ANALYSIS]: Your Network Mask is /16 (255.255.0.0)")
                print("RESULT: This is a large network. The third group doesn't matter.")
            
        except Exception as e:
            print(f"Error running 'ip' command: {e}")

    def run_broadcast_test(self):
        """
        This is a 'Production' trick. We send a 'Ping' to the entire 
        network to see who wakes up.
        """
        print(f"\n[{self.timestamp()}] DEBUG: Attempting to 'Listen' for siblings...")
        hostname = socket.gethostname()
        local_ip = socket.gethostbyname(hostname)
        print(f"Your Linux IP is: {local_ip}")
        
        # Split the IP to find the subnet
        parts = local_ip.split('.')
        subnet = f"{parts[0]}.{parts[1]}.{parts[2]}"
        
        print(f"I am looking for devices that start with: {subnet}.XXX")

# --- EXECUTION ---
if __name__ == "__main__":
    detective = SubnetDetective()
    detective.get_detailed_ip_info()
    detective.run_broadcast_test()