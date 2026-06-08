#!/usr/bin/env python3
"""
Linux Security & User Auditor
-----------------------------
Architecture: Modular, Event-Driven
Focus: Environment Variables, Log Parsing, Permission Trapping
"""

import os            # Interacting with the OS environment
import subprocess    # Executing Linux CLI tools
import sys           # System-specific parameters and functions
from datetime import datetime
import json

class LinuxAuditor:
    def __init__(self):
        """
        Constructor: Prepares the audit report.
        """
        print(f"[{datetime.now()}] DEBUG: Auditor Engine Started.")
        self.audit_results = {}

    def get_user_environment(self):
        """
        ROOT CAUSE: Linux uses Environment Variables to define the workspace.
        This method extracts specific data about the current session.
        """
        print(f"[{datetime.now()}] DEBUG: Fetching Environment Data...")
        try:
            # os.environ is a dictionary of all Linux environment variables
            self.audit_results['current_user'] = os.environ.get('USER', 'Unknown')
            self.audit_results['shell'] = os.environ.get('SHELL', 'Unknown')
            self.audit_results['home_dir'] = os.environ.get('HOME', 'Unknown')
            
            # We can also check if the script is running as 'root' (UID 0)
            # This is critical for production scripts that need high privileges
            self.audit_results['is_root'] = (os.geteuid() == 0)
            
            print(f"[{datetime.now()}] SUCCESS: Environment variables mapped.")
        except Exception as e:
            print(f"[{datetime.now()}] ERROR: Could not map environment: {e}")

    def check_login_history(self):
        """
        ROOT CAUSE: Security auditing requires knowing who logged in recently.
        On Linux, the 'last' command reads the binary file /var/log/wtmp.
        """
        print(f"[{datetime.now()}] DEBUG: Reading login history via 'last' command...")
        try:
            # We run 'last -n 5' to get the last 5 login events
            raw_last = subprocess.check_output(["last", "-n", "5"]).decode("utf-8")
            
            # We split the lines and clean up the whitespace
            history = [line.strip() for line in raw_last.split('\n') if line.strip()]
            self.audit_results['recent_logins'] = history
            print(f"[{datetime.now()}] SUCCESS: Login history retrieved.")
        except subprocess.CalledProcessError as e:
            print(f"[{datetime.now()}] ERROR: Failed to run 'last': {e}")
            self.audit_results['recent_logins'] = "Permission Denied/Error"

    def scan_for_system_errors(self):
        """
        ROOT CAUSE: System health issues are logged to 'dmesg' (Kernel ring buffer).
        We will scan the last 50 lines of dmesg for keywords like 'fail' or 'error'.
        """
        print(f"[{datetime.now()}] DEBUG: Scanning Kernel Buffer (dmesg) for errors...")
        found_errors = []
        
        try:
            # We use 'dmesg' to get kernel logs. 
            # Note: On some systems, this requires sudo. We will trap that.
            raw_dmesg = subprocess.check_output(["dmesg", "--level=err,warn"]).decode("utf-8")
            
            for line in raw_dmesg.split('\n')[-20:]: # Look at the last 20 errors/warnings
                if line.strip():
                    found_errors.append(line.strip())
            
            self.audit_results['system_warnings'] = found_errors if found_errors else "No errors found."
            print(f"[{datetime.now()}] SUCCESS: Kernel scan complete.")
            
        except subprocess.CalledProcessError:
            # TRAPPING: Pop!_OS/Ubuntu often restricts dmesg to root.
            print(f"[{datetime.now()}] WARNING: 'dmesg' access denied. Try running with sudo?")
            self.audit_results['system_warnings'] = "Access Denied (Requires Root)"
        except Exception as e:
            print(f"[{datetime.now()}] ERROR: Unexpected log scan error: {e}")

    def run_audit(self):
        """
        Orchestrator to execute the logic modules.
        """
        print("\n" + "="*40)
        print("LINUX SECURITY AUDIT IN PROGRESS")
        print("="*40)
        
        self.get_user_environment()
        self.check_login_history()
        self.scan_for_system_errors()
        
        print("="*40)
        print("AUDIT COMPLETE\n")

    def print_final_report(self):
        """
        Outputs results in a structured format.
        """
        # Using json.dumps makes the Python Dictionary look beautiful
        formatted_json = json.dumps(self.audit_results, indent=4)
        print(formatted_json)

# --- EXECUTION ---
if __name__ == "__main__":
    # Create the object
    my_auditor = LinuxAuditor()
    
    # Run the logic
    try:
        my_auditor.run_audit()
        my_auditor.print_final_report()
    except Exception as e:
        print(f"FATAL: Auditor crashed: {e}")
        sys.exit(1) # Return a non-zero exit code to the Linux Shell