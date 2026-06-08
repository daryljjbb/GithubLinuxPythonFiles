#!/usr/bin/env python3
"""
Linux Python Media Streamer (V3 - Multi-Device Support)
------------------------------------------------------
Architecture: ThreadingHTTPServer (Supports multiple concurrent users)
Focus: Firewall debugging, Multi-threading, and Connection Logging.
"""

import http.server
import socketserver
import os
import socket
import getpass
from datetime import datetime

# --- CONFIGURATION ---
REAL_USER = os.getenv("SUDO_USER") or getpass.getuser()
MEDIA_DIRECTORY = f"/home/{REAL_USER}/Videos"
PORT = 8888 

class ThreadedMediaHandler(http.server.SimpleHTTPRequestHandler):
    """
    Handles requests from multiple devices simultaneously.
    """
    
    def log_message(self, format, *args):
        """
        OVERRIDE: This prints every time a device (like your iPhone) 
        reaches out to the server. Great for debugging connectivity!
        """
        print(f"[{datetime.now().strftime('%H:%M:%S')}] ACCESS: {self.address_string()} requested {args[0]}")

    def list_directory(self, path):
        """
        Generates the mobile-friendly HTML interface.
        """
        print(f"[{datetime.now()}] DEBUG: Generating menu for {self.address_string()}")
        
        try:
            # We list files in the current working directory
            files = sorted(os.listdir("."))
        except Exception as e:
            return None

        html = f"""
        <html>
        <head>
            <meta name="viewport" content="width=device-width, initial-scale=1">
            <title>Linux Home Server</title>
            <style>
                body {{ font-family: sans-serif; background: #121212; color: white; padding: 20px; }}
                h1 {{ color: #00ff88; }}
                .file-card {{ 
                    display: block; background: #222; border-left: 5px solid #00ff88;
                    margin: 10px 0; padding: 20px; color: white; 
                    text-decoration: none; border-radius: 5px;
                }}
            </style>
        </head>
        <body>
            <h1>Media Library</h1>
            <p>Connected from: {self.address_string()}</p>
        """

        valid_exts = ('.mp4', '.mkv', '.mp3', '.wav')
        for f in files:
            if f.lower().endswith(valid_exts):
                html += f'<a class="file-card" href="{f}">播放 (Play) {f}</a>'
        
        html += "</body></html>"
        
        encoded = html.encode("utf-8", "surrogateescape")
        self.send_response(200)
        self.send_header("Content-type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(encoded)))
        self.end_headers()
        self.wfile.write(encoded)
        return None

# ROOT CAUSE FIX: We use ThreadingMixIn to handle multiple devices at once
class ThreadingSimpleServer(socketserver.ThreadingMixIn, socketserver.TCPServer):
    """
    This class allows the server to 'split' into multiple threads.
    If your iPhone is downloading a video, the server can still 
    talk to your Linux browser at the same time.
    """
    pass

def get_ip():
    """Finds the LAN IP address of your Pop!_OS machine."""
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(('8.8.8.8', 1))
        return s.getsockname()[0]
    except:
        return '127.0.0.1'
    finally:
        s.close()

def start_server():
    # 1. Path Safety Check
    if not os.path.exists(MEDIA_DIRECTORY):
        print(f"[!] ERROR: {MEDIA_DIRECTORY} not found.")
        return

    os.chdir(MEDIA_DIRECTORY)
    
    # 2. Server Initialization
    # Bind to "" (empty string) means listen on ALL network cards (Wifi + Ethernet)
    server_address = ("", PORT)
    
    print(f"[{datetime.now()}] DEBUG: Starting Threaded Engine...")
    
    try:
        with ThreadingSimpleServer(server_address, ThreadedMediaHandler) as httpd:
            my_ip = get_ip()
            print("\n" + "═"*50)
            print("🎬 MULTI-DEVICE MEDIA SERVER IS RUNNING")
            print(f"1. Ensure iPhone is on the SAME Wi-Fi as this PC.")
            print(f"2. On iPhone Safari, go to: http://{my_ip}:{PORT}")
            print(f"3. Check 'sudo ufw status' if it still fails.")
            print("═"*50 + "\n")
            
            httpd.serve_forever()
    except Exception as e:
        print(f"[!] FATAL ERROR: {e}")

if __name__ == "__main__":
    start_server()