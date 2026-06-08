#!/usr/bin/env python3
"""
DEFINITIVE LINUX NETWORK SHARK
------------------------------
Installation Requirements:
1. Update system:       sudo apt update
2. Install Pip:         sudo apt install python3-pip
3. Install Scapy:       sudo python3 -m pip install scapy  <-- CRITICAL (Install as Root)

Usage:
Run with: sudo python3 shark.py
"""

import os
import sys
import time
import json
from datetime import datetime

# --- ERROR TRAPPING FOR LIBRARIES ---
try:
    # Scapy is the engine that talks to the Linux Network Stack
    from scapy.all import sniff, IP, TCP, UDP, ICMP
    print(f"[{datetime.now()}] DEBUG: Network libraries loaded successfully.")
except ImportError:
    print("\n" + "!"*60)
    print("FATAL ERROR: Scapy library not found for the ROOT user.")
    print("ROOT CAUSE: You likely installed scapy as a standard user.")
    print("FIX: Run the following command:")
    print("     sudo python3 -m pip install scapy")
    print("!"*60 + "\n")
    sys.exit(1)

class LinuxNetworkShark:
    """
    A modular, production-ready network sniffer for Linux.
    Designed to be scalable and memory-efficient.
    """
    
    def __init__(self, filter_rule="tcp and port 443"):
        """
        Initialize the Shark.
        :param filter_rule: BPF (Berkeley Packet Filter) string.
                            Common filters:
                            - "tcp" (All TCP traffic)
                            - "udp" (All UDP traffic)
                            - "port 80" (HTTP traffic)
                            - "icmp" (Ping requests)
        """
        self.packet_count = 0
        self.start_time = None
        self.filter_rule = filter_rule
        print(f"[{datetime.now()}] DEBUG: Shark Object created. Filter: '{self.filter_rule}'")

    def packet_callback(self, packet):
        """
        ROOT CAUSE EXPLANATION:
        This function is the 'Observer'. Every time the Linux Kernel sees a 
        packet matching our filter, it 'interrupts' Python and runs this code.
        """
        try:
            if packet.haslayer(IP):
                self.packet_count += 1
                
                # Extracting Core Data
                src_ip = packet[IP].src
                dst_ip = packet[IP].dst
                pkt_size = len(packet)
                
                # Determine Protocol String
                if packet.haslayer(TCP):
                    proto = "TCP"
                elif packet.haslayer(UDP):
                    proto = "UDP"
                elif packet.haslayer(ICMP):
                    proto = "ICMP"
                else:
                    proto = "IP"

                # LOGGING: Using a structured format for easy debugging
                timestamp = datetime.now().strftime('%H:%M:%S.%f')[:-3]
                print(f"[{timestamp}] PKT #{self.packet_count} | {proto} | {src_ip} --> {dst_ip} | Size: {pkt_size} bytes")
                
        except Exception as e:
            # TRAPPING: If a weirdly formatted packet arrives, don't crash the script
            print(f"[{datetime.now()}] ERROR: Could not parse packet: {e}")

    def run(self):
        """
        Checks permissions and starts the sniffing loop.
        """
        print(f"[{datetime.now()}] DEBUG: Checking system permissions...")

        # ROOT CAUSE: Linux protects raw sockets. Only UID 0 (Root) can open them.
        if os.getuid() != 0:
            print("\n" + "="*50)
            print("PERMISSION DENIED")
            print("ROOT CAUSE: This script accesses the raw network interface.")
            print("FIX: Run with: sudo python3 shark.py")
            print("="*50 + "\n")
            return

        print("\n" + "═"*60)
        print("LINUX SHARK MONITOR ACTIVE")
        print(f"Started at: {datetime.now()}")
        print(f"Filter: {self.filter_rule}")
        print("═"*60 + "\n")

        self.start_time = time.time()

        try:
            # sniff() is the heavy lifter.
            # filter: Uses BPF (Kernel-level filtering) for high speed.
            # prn: The function to call for every packet.
            # store=0: IMPORTANT! Does not keep packets in RAM. 
            #          Without this, your Linux machine will crash after 1 hour of sniffing.
            sniff(
                filter=self.filter_rule, 
                prn=self.packet_callback, 
                store=0
            )
        except Exception as e:
            print(f"[{datetime.now()}] CRITICAL: Sniffer Engine Failed: {e}")

    def print_final_stats(self):
        """
        Calculates and displays session summary.
        """
        if self.start_time:
            duration = round(time.time() - self.start_time, 2)
            print("\n" + "═"*60)
            print("SESSION SUMMARY")
            print(f"Total Packets Captured: {self.packet_count}")
            print(f"Total Duration: {duration} seconds")
            if duration > 0:
                print(f"Avg Packets/Sec: {round(self.packet_count / duration, 2)}")
            print("═"*60)

# --- EXECUTION ---
if __name__ == "__main__":
    # 1. Create the Instance
    # You can change the filter here! (e.g., "icmp", "udp", "port 80")
    my_shark = LinuxNetworkShark(filter_rule="tcp and port 443")

    try:
        # 2. Run the Engine
        my_shark.run()
    except KeyboardInterrupt:
        # 3. Graceful Exit (Trap Ctrl+C)
        print(f"\n[{datetime.now()}] DEBUG: User requested shutdown.")
        my_shark.print_final_stats()
        print("Exiting safely.")
        sys.exit(0)