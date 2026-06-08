#!/usr/bin/env python3
"""
Linux File Integrity Monitor (FIM)
----------------------------------
Architecture: Event-Loop / Observer Pattern
Focus: Cryptographic Hashing, File Metadata, Polling Logic
"""

import os            # For file path and metadata operations
import hashlib       # For generating SHA-256 fingerprints
import time          # For controlling the loop frequency
import json          # For logging the state
from datetime import datetime

class FileIntegrityMonitor:
    def __init__(self, watch_path):
        """
        Initialize the monitor with a target directory.
        """
        self.watch_path = watch_path
        # This dictionary will store our 'Baseline' (The 'Correct' state of files)
        self.baseline = {}
        print(f"[{datetime.now()}] DEBUG: FIM Initialized for path: {watch_path}")

    def calculate_sha256(self, file_path):
        """
        ROOT CAUSE: We read the file in 'binary mode' (rb) and 
        create a SHA-256 hash. This is the only way to guarantee 
        the file content is identical.
        """
        sha256_hash = hashlib.sha256()
        try:
            with open(file_path, "rb") as f:
                # Read the file in chunks so we don't crash if the file is huge (GBs)
                for byte_block in iter(lambda: f.read(4096), b""):
                    sha256_hash.update(byte_block)
            return sha256_hash.hexdigest()
        except PermissionError:
            print(f"[{datetime.now()}] ERROR: Permission denied on {file_path}")
            return "Permission Denied"
        except FileNotFoundError:
            return "Deleted"

    def create_baseline(self):
        """
        Scans the directory and saves the current state of all files.
        This is what we compare against later.
        """
        print(f"[{datetime.now()}] DEBUG: Generating initial baseline...")
        
        if not os.path.exists(self.watch_path):
            print(f"[{datetime.now()}] CRITICAL: Path {self.watch_path} does not exist!")
            return

        for root, dirs, files in os.walk(self.watch_path):
            for name in files:
                full_path = os.path.join(root, name)
                file_hash = self.calculate_sha256(full_path)
                self.baseline[full_path] = file_hash
        
        print(f"[{datetime.now()}] SUCCESS: Baseline created for {len(self.baseline)} files.")

    def monitor(self, interval_seconds=5):
        """
        The main loop. This will run forever until you press Ctrl+C.
        """
        print(f"[{datetime.now()}] SUCCESS: Monitoring started. Press Ctrl+C to stop.")
        
        try:
            while True:
                # 1. Wait for the specified interval
                time.sleep(interval_seconds)
                
                # 2. Get the current state of the folder
                current_files = []
                for root, dirs, files in os.walk(self.watch_path):
                    for name in files:
                        full_path = os.path.join(root, name)
                        current_files.append(full_path)
                        
                        # Calculate current hash
                        current_hash = self.calculate_sha256(full_path)
                        
                        # CHECK 1: Is this a new file?
                        if full_path not in self.baseline:
                            print(f"\n[{datetime.now()}] ALERT: NEW FILE CREATED: {full_path}")
                            self.baseline[full_path] = current_hash
                        
                        # CHECK 2: Has the content changed?
                        elif current_hash != self.baseline[full_path]:
                            print(f"\n[{datetime.now()}] ALERT: FILE MODIFIED: {full_path}")
                            # Update the baseline so we don't alert again for the same change
                            self.baseline[full_path] = current_hash
                
                # CHECK 3: Was a file deleted?
                # We create a list of keys to delete to avoid "RuntimeError: dictionary changed size"
                deleted_files = []
                for recorded_path in self.baseline:
                    if recorded_path not in current_files:
                        print(f"\n[{datetime.now()}] ALERT: FILE DELETED: {recorded_path}")
                        deleted_files.append(recorded_path)
                
                for path in deleted_files:
                    del self.baseline[path]

        except KeyboardInterrupt:
            print(f"\n[{datetime.now()}] DEBUG: Stopping monitor...")

# --- EXECUTION BLOCK ---
if __name__ == "__main__":
    # For this exercise, let's watch your 'Linux' folder.
    # We use os.getcwd() to get the folder you are currently in.
    current_dir = os.getcwd()
    
    # Instantiate the monitor
    fim = FileIntegrityMonitor(current_dir)
    
    # 1. Take a 'Snapshot' of the folder
    fim.create_baseline()
    
    # 2. Start watching for changes every 2 seconds
    try:
        fim.monitor(interval_seconds=2)
    except Exception as e:
        print(f"FATAL ERROR: {e}")