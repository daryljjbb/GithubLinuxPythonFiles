#!/usr/bin/env python3
"""
Linux Firewall Controller (UFW Manager)
---------------------------------------
Architecture: Subprocess Wrapper with Logic Trapping
Focus: Managing the 'Active/Inactive' state and cleaning up rules.
"""

import subprocess
import os
import sys
from datetime import datetime

class FirewallManager:
    def __init__(self):
        """
        Initialize the manager and check for Root privileges.
        """
        self.timestamp = lambda: datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f"[{self.timestamp()}] DEBUG: Firewall Manager Initialized.")
        
        # ROOT CAUSE: UFW commands require root (UID 0)
        if os.getuid() != 0:
            print(f"[{self.timestamp()}] CRITICAL: This script must be run with 'sudo'.")
            sys.exit(1)

    def run_command(self, cmd_list):
        """
        ROOT CAUSE: A helper to run Linux CLI commands and trap errors.
        """
        print(f"[{self.timestamp()}] EXECUTING: {' '.join(cmd_list)}")
        try:
            # capture_output=True lets us read what the command says back to us
            result = subprocess.run(cmd_list, capture_output=True, text=True, check=True)
            return result.stdout.strip()
        except subprocess.CalledProcessError as e:
            print(f"[{self.timestamp()}] ERROR: Command failed: {e.stderr}")
            return None

    def get_status(self):
        """
        Checks if the firewall is Active or Inactive.
        """
        output = self.run_command(['ufw', 'status'])
        if "inactive" in output.lower():
            print(f"[{self.timestamp()}] STATUS: Firewall is currently OFF (Inactive).")
            return False
        else:
            print(f"[{self.timestamp()}] STATUS: Firewall is currently ON (Active).")
            return True

    def toggle_firewall(self, enable=True):
        """
        Turns the firewall on or off.
        """
        action = "enable" if enable else "disable"
        print(f"[{self.timestamp()}] DEBUG: Changing firewall state to: {action.upper()}")
        
        # When enabling, Linux asks for confirmation. '--force' bypasses the prompt.
        result = self.run_command(['ufw', '--force', action])
        print(f"[{self.timestamp()}] SUCCESS: {result}")

    def clean_rule(self, port="8888"):
        """
        Specifically deletes the media server rule.
        """
        print(f"[{self.timestamp()}] DEBUG: Removing rule for port {port}")
        result = self.run_command(['ufw', 'delete', 'allow', f'{port}/tcp'])
        if result:
            print(f"[{self.timestamp()}] SUCCESS: {result}")

    def full_security_reset(self):
        """
        Returns the firewall to its original Linux factory state.
        """
        print("\n" + "="*50)
        print("PERFORMING FULL FIREWALL RESET")
        print("="*50)
        
        # 1. Delete the specific media rule
        self.clean_rule("8888")
        
        # 2. Disable the firewall (Original Status)
        self.toggle_firewall(enable=False)
        
        print("\n[!] System is now back to its original state.")
        print("="*50 + "\n")

# --- MAIN EXECUTION ---
if __name__ == "__main__":
    manager = FirewallManager()
    
    print("\n--- FIREWALL MANAGEMENT MENU ---")
    print("1. View Current Status")
    print("2. Enable Firewall (Security Mode)")
    print("3. Disable Firewall (Original/Open Mode)")
    print("4. RESET TO ORIGINAL (Delete 8888 & Disable)")
    print("5. Exit")
    
    try:
        choice = input("\nSelect an option (1-5): ")
        
        if choice == "1":
            status = manager.get_status()
            # If active, show the rules
            if status:
                print(manager.run_command(['ufw', 'status']))
        
        elif choice == "2":
            manager.toggle_firewall(enable=True)
            
        elif choice == "3":
            manager.toggle_firewall(enable=False)
            
        elif choice == "4":
            manager.full_security_reset()
            
        elif choice == "5":
            print("Exiting...")
            
        else:
            print("Invalid choice.")

    except KeyboardInterrupt:
        print("\nShutdown requested.")