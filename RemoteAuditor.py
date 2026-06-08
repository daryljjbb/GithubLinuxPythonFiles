#!/usr/bin/env python3
"""
Linux Remote-Ready Auditor
--------------------------
Architecture: Network Interface & WAN Discovery
Focus: Identifying Public IPs and VPN Tunneling (Tailscale/Wireguard).
"""

import socket
import subprocess
import os
import json
import urllib.request # Used to talk to the 'Outside' world
from datetime import datetime

class RemoteAuditor:
    def __init__(self):
        self.report = {}
        print(f"[{datetime.now()}] DEBUG: Starting Remote Readiness Audit...")

    def get_public_ip(self):
        """
        ROOT CAUSE: Your Linux PC doesn't actually know its own Public IP.
        We have to ask a server on the internet 'What do I look like to you?'
        """
        print(f"[{datetime.now()}] DEBUG: Contacting IP Check service...")
        try:
            # We use an external service to find our 'Front Door' address
            with urllib.request.urlopen('https://ident.me', timeout=5) as response:
                self.report['public_ip'] = response.read().decode('utf-8')
            print(f"[{datetime.now()}] SUCCESS: Public IP detected.")
        except Exception as e:
            self.report['public_ip'] = "Error: Offline or Blocked"
            print(f"[{datetime.now()}] WARNING: Could not find Public IP: {e}")

    def check_for_tunnels(self):
        """
        ROOT CAUSE: Professional remote access uses 'Tunnels' (interfaces like utun or tailscale0).
        This checks if a secure tunnel is currently active.
        """
        print(f"[{datetime.now()}] DEBUG: Scanning Linux Network Interfaces...")
        try:
            # Run the Linux 'ip addr' command
            result = subprocess.check_output(["ip", "addr"]).decode('utf-8')
            
            # Look for common VPN/Tunnel names
            if "tailscale" in result.lower():
                self.report['tunnel_type'] = "Tailscale (Secure)"
            elif "wg0" in result.lower():
                self.report['tunnel_type'] = "WireGuard (Secure)"
            elif "tun0" in result.lower():
                self.report['tunnel_type'] = "OpenVPN (Standard)"
            else:
                self.report['tunnel_type'] = "None (LAN Only)"
                
        except Exception as e:
            print(f"ERROR: Could not scan interfaces: {e}")

    def audit_firewall(self):
        """
        Ensures the firewall is set up to handle traffic on the Media Port.
        """
        try:
            status = subprocess.check_output(["sudo", "ufw", "status"]).decode('utf-8')
            self.report['firewall_active'] = "inactive" not in status.lower()
            self.report['port_5000_open'] = "5000" in status
        except:
            self.report['firewall_error'] = "Check Sudo Permissions"

    def run_audit(self):
        self.get_public_ip()
        self.check_for_tunnels()
        self.audit_firewall()
        
        print("\n" + "="*50)
        print("REMOTE ACCESS READINESS REPORT")
        print("="*50)
        print(json.dumps(self.report, indent=4))
        print("="*50)

        # LOGIC CHECK
        if self.report['tunnel_type'] == "None (LAN Only)":
            print("\n[!] RECOMMENDATION: Your PC is currently invisible to the internet.")
            print("To connect from your iPhone remotely, install 'Tailscale' on both devices.")
        else:
            print(f"\n[OK] You are using {self.report['tunnel_type']}.")
            print("You can use your Tunnel IP to access the dashboard from anywhere!")

if __name__ == "__main__":
    auditor = RemoteAuditor()
    auditor.run_audit()