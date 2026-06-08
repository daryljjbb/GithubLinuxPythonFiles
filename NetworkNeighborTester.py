#!/usr/bin/env python3
"""
Linux Network Neighbor Tester
-----------------------------
Architecture: ICMP Ping + Socket Diagnostics
Focus: Verifying if '10.16.55' can talk to '10.16.59'
"""

import os
import platform
import subprocess
import socket
from datetime import datetime

class NetworkNeighborTester:
    def __init__(self, target_ip):
        self.target_ip = target_ip
        self.timestamp = lambda: datetime.now().strftime("%H:%M:%S")

    def ping_test(self):
        """
        ROOT CAUSE: Ping uses 'ICMP' packets. 
        If Ping fails, the 'Subnet Wall' is likely blocking all traffic.
        """
        print(f"[{self.timestamp()}] DEBUG: Attempting to 'Ping' iPhone at {self.target_ip}")
        
        # '-c 1' means send 1 packet. '-W 2' means wait 2 seconds for a reply.
        command = ["ping", "-c", "1", "-W", "2", self.target_ip]
        
        try:
            # We run the system ping command
            output = subprocess.run(command, capture_output=True, text=True)
            
            if output.returncode == 0:
                print(f"[{self.timestamp()}] SUCCESS: iPhone is REACHABLE via Ping!")
                return True
            else:
                print(f"[{self.timestamp()}] FAILURE: iPhone is NOT reachable.")
                print(f"REASON: Your router is blocking traffic between .55 and .59 subnets.")
                return False
        except Exception as e:
            print(f"[{self.timestamp()}] ERROR: Ping command failed: {e}")
            return False

    def check_subnet_mask(self):
        """
        ROOT CAUSE: Identifying if we are in a /16 or /24 network.
        """
        print(f"[{self.timestamp()}] DEBUG: Checking Linux Network Mask...")
        try:
            # We look for the line containing our IP
            result = subprocess.check_output(["ip", "-4", "addr", "show"]).decode()
            for line in result.split('\n'):
                if "10.16.55" in line:
                    print(f"[{self.timestamp()}] NETWORK CONFIG: {line.strip()}")
                    if "/24" in line:
                        print("RESULT: You are on a /24 Subnet. .55 and .59 CANNOT talk by default.")
                    elif "/16" in line:
                        print("RESULT: You are on a /16 Subnet. They SHOULD be able to talk.")
        except Exception as e:
            print(f"Could not parse IP info: {e}")

    def run_diagnostic(self):
        print("="*60)
        print(f"DIAGNOSING: Linux (10.16.55) --> iPhone ({self.target_ip})")
        print("="*60)
        
        self.check_subnet_mask()
        reachable = self.ping_test()
        
        print("\n" + "="*60)
        if reachable:
            print("CONCLUSION: The network is open! The iPhone issue is Safari/Software.")
        else:
            print("CONCLUSION: The Network/Router is blocking you.")
            print("FIX: Move both devices to the same Wi-Fi Band (e.g. both on 'Home_Wi-Fi').")
        print("="*60)

if __name__ == "__main__":
    # INSTRUCTION: Enter your iPhone's FULL IP address here
    IPHONE_IP = "10.16.59.XXX" # <--- Put the full iPhone IP here
    
    tester = NetworkNeighborTester(IPHONE_IP)
    tester.run_diagnostic()