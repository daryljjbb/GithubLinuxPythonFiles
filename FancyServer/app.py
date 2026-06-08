#!/usr/bin/env python3
"""
Fancy Linux Media Dashboard (V2 - Path Fixed)
---------------------------------------------
Architecture: Flask Web Framework
Focus: Solving the 'Sudo Home' pathing issue and improving UI data.
"""

from flask import Flask, render_template, send_from_directory
import os
import socket
import psutil
import getpass
from datetime import datetime

app = Flask(__name__)

# --- ROOT CAUSE FIX: DYNAMIC PATHING ---
# If we run with 'sudo', os.getenv("SUDO_USER") will be 'darylbusson'.
# If we run normally, getpass.getuser() will be 'darylbusson'.
REAL_USER = os.getenv("SUDO_USER") or getpass.getuser()
MEDIA_FOLDER = f"/home/{REAL_USER}/Videos"

def get_sys_stats():
    """
    Fetches live Linux performance data.
    """
    try:
        return {
            "cpu": psutil.cpu_percent(interval=None),
            "ram": psutil.virtual_memory().percent,
            "disk": psutil.disk_usage('/').percent,
            "uptime": datetime.now().strftime("%H:%M:%S"),
            "user": REAL_USER
        }
    except Exception as e:
        print(f"[{datetime.now()}] STATS ERROR: {e}")
        return {"cpu": 0, "ram": 0, "disk": 0, "uptime": "Error", "user": REAL_USER}

@app.route('/')
def dashboard():
    """
    Main page route.
    """
    print(f"[{datetime.now()}] DEBUG: Dashboard requested by {REAL_USER}")
    
    media_files = []
    error_msg = None

    # 1. Check if the folder actually exists
    if not os.path.exists(MEDIA_FOLDER):
        error_msg = f"Folder not found: {MEDIA_FOLDER}"
        print(f"[{datetime.now()}] CRITICAL: {error_msg}")
    else:
        # 2. Try to list files
        try:
            all_items = os.listdir(MEDIA_FOLDER)
            media_files = [f for f in all_items if f.lower().endswith(('.mp4', '.mkv', '.mp3', '.mov'))]
            print(f"[{datetime.now()}] SUCCESS: Found {len(media_files)} files in {MEDIA_FOLDER}")
        except PermissionError:
            error_msg = "Permission Denied: Cannot read the Videos folder."
        except Exception as e:
            error_msg = f"Unexpected Error: {e}"

    stats = get_sys_stats()

    # We pass 'error_msg' to the HTML so the user sees it on their iPhone
    return render_template('index.html', files=media_files, stats=stats, error=error_msg)

@app.route('/stream/<filename>')
def stream_file(filename):
    """
    Sends the raw video data to the browser.
    """
    print(f"[{datetime.now()}] DEBUG: Streaming file -> {filename}")
    # send_from_directory is the secure way to serve files in Flask
    return send_from_directory(MEDIA_FOLDER, filename)

def get_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(('8.8.8.8', 1))
        return s.getsockname()[0]
    except: return '127.0.0.1'
    finally: s.close()

if __name__ == '__main__':
    ip = get_ip()
    print("\n" + "═"*50)
    print("🚀 FANCY DASHBOARD: VERSION 2 (PATH FIXED)")
    print(f"Targeting: {MEDIA_FOLDER}")
    print(f"iPhone URL: http://{ip}:5000")
    print("═"*50 + "\n")
    
    # Debug=True is great for learning because it restarts the server 
    # automatically when you save changes to this file.
    app.run(host='0.0.0.0', port=5000, debug=True)