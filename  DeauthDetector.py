#!/usr/bin/env python3
"""
Linux Wi-Fi Deauth Attack Detector
----------------------------------
Architecture: Real-time Wireless Packet Inspection
Focus: 802.11 Management Frames, Monitor Mode, Attack Signatures

REQUIREMENT: Your Wi-Fi card MUST be in 'Monitor Mode'.
"""

import os
import sys
from datetime import datetime

# --- ERROR TRAPPING: LIBRARIES ---
try:
    # Dot11 is the Scapy class for 802.11 (Wi-Fi) packets
    from scapy.all import sniff, Dot11, Dot11Deauth, Dot11Disas
    print(f"[{datetime.now()}] SUCCESS: Wireless libraries loaded.")
except ImportError:
    print("\n[!] ERROR: Scapy not found. Run: sudo python3 -m pip install scapy\n")
    sys.exit(1)

class DeauthDetector:
    def __init__(self, interface):
        """
        :param interface: The monitor mode interface (e.g., 'wlan0mon')
        """
        self.interface = interface
        self.attack_count = 0
        # Threshold: How many packets before we consider it a 'Flood'
        self.threshold = 5 
        print(f"[{datetime.now()}] DEBUG: Detector initialized on {interface}")

    def process_packet(self, pkt):
        """
        ROOT CAUSE EXPLANATION:
        We are looking for Dot11 (Wi-Fi) packets that have the 
        'Deauthentication' (Subtype 12) or 'Disassociation' (Subtype 10) flag.
        """
        # Check if the packet is a Wi-Fi Management Frame
        if pkt.haslayer(Dot11):
            # Check specifically for Deauth (Type 0, Subtype 12) 
            # or Disassociation (Type 0, Subtype 10)
            if pkt.haslayer(Dot11Deauth) or pkt.haslayer(Dot11Disas):
                
                self.attack_count += 1
                
                # Extract MAC addresses
                # Addr1 = Receiver, Addr2 = Transmitter, Addr3 = Access Point ID
                target = pkt.addr1
                source = pkt.addr2
                
                print(f"\n[!] ALERT: Deauth Frame Detected!")
                print(f"    Timestamp: {datetime.now()}")
                print(f"    Source (Spoofed AP): {source}")
                print(f"    Target (Victim):    {target}")
                print(f"    Total Seen:         {self.attack_count}")

                if self.attack_count > self.threshold:
                    print(">>> WARNING: HIGH-INTENSITY ATTACK IN PROGRESS (FLOODING) <<<")

    def start(self):
        """
        Verify Root and start the sniffer.
        """
        # ROOT CAUSE: Wireless sniffing requires hardware-level access (Root)
        if os.getuid() != 0:
            print("\n[!] ERROR: Must run as Root/Sudo to access Wi-Fi hardware.")
            return

        print("\n" + "="*60)
        print(f"WIFI DEAUTH DETECTOR STARTING ON {self.interface}")
        print("Requirement: Monitor Mode must be enabled.")
        print("Press Ctrl+C to stop monitoring.")
        print("="*60 + "\n")

        try:
            # We use 'sniff' but specifically target the monitor interface
            # 'store=0' ensures we don't run out of RAM during a flood
            sniff(iface=self.interface, prn=self.process_packet, store=0)
        except Exception as e:
            print(f"CRITICAL: Failed to sniff on {self.interface}: {e}")
            print("Is your interface in Monitor Mode? Check with 'iwconfig'.")

# --- MAIN EXECUTION ---
if __name__ == "__main__":
    # INSTRUCTION: Replace 'wlan0mon' with your actual monitor interface name
    # You find this by running 'iwconfig' in your terminal.
    # On Pop!_OS, it might be something like 'wlp2s0' or 'wlan0mon'
    MONITOR_INTERFACE = "wlan0mon" 

    detector = DeauthDetector(interface=MONITOR_INTERFACE)
    
    try:
        detector.start()
    except KeyboardInterrupt:
        print(f"\n[{datetime.now()}] Monitoring stopped.")
        print(f"Final Count: {detector.attack_count} malicious frames detected.")
        sys.exit(0)