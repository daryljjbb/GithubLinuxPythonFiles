#!/usr/bin/env python3
"""
Professional Linux Media Hub (V4 - Persistent Watch History)
-----------------------------------------------------------
Architecture: Flask + SQLite3 Database
Focus: SQL Integration, Data Persistence, and Logic Auditing.
"""

from flask import Flask, render_template, send_from_directory, request, Response
import os
import sqlite3
import subprocess
import psutil
import getpass
from datetime import datetime

app = Flask(__name__)

# --- CONFIGURATION & PATHS ---
REAL_USER = os.getenv("SUDO_USER") or getpass.getuser()
MEDIA_FOLDER = f"/home/{REAL_USER}/Videos"
THUMBNAIL_FOLDER = os.path.join(app.root_path, 'static', 'thumbnails')
DATABASE_FILE = os.path.join(app.root_path, 'history.db')
PASSWORD = "linux"

os.makedirs(THUMBNAIL_FOLDER, exist_ok=True)

# --- DATABASE LOGIC ---
def init_db():
    """
    ROOT CAUSE: We need a 'Table' to store our history.
    This creates the history.db file if it doesn't exist.
    """
    print(f"[{datetime.now()}] DEBUG: Initializing SQLite Database...")
    conn = sqlite3.connect(DATABASE_FILE)
    cursor = conn.cursor()
    # Create a table with: ID, Filename, and Timestamp
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            filename TEXT NOT NULL,
            watched_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.commit()
    conn.close()

def log_watch_event(filename):
    """
    ROOT CAUSE: Every time a stream starts, we record it in the DB.
    """
    try:
        conn = sqlite3.connect(DATABASE_FILE)
        cursor = conn.cursor()
        cursor.execute("INSERT INTO history (filename) VALUES (?)", (filename,))
        conn.commit()
        conn.close()
        print(f"[{datetime.now()}] SUCCESS: Logged {filename} to watch history.")
    except Exception as e:
        print(f"[{datetime.now()}] ERROR: Could not log to DB: {e}")

def get_recent_history():
    """
    Fetches the last 5 items watched.
    """
    try:
        conn = sqlite3.connect(DATABASE_FILE)
        cursor = conn.cursor()
        # SQL query: Order by time descending, limit to 5
        cursor.execute("SELECT filename, watched_at FROM history ORDER BY watched_at DESC LIMIT 5")
        rows = cursor.fetchall()
        conn.close()
        return rows
    except:
        return []

# --- MEDIA LOGIC (FROM PREVIOUS STEPS) ---
def generate_thumbnail(video_path, thumb_name):
    thumb_path = os.path.join(THUMBNAIL_FOLDER, thumb_name)
    if os.path.exists(thumb_path): return
    try:
        cmd = ['ffmpeg', '-i', video_path, '-ss', '00:00:01', '-vframes', '1', thumb_path, '-y']
        subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    except: pass

# --- SECURITY LOGIC ---
def check_auth(username, password): return password == PASSWORD
def authenticate():
    return Response('Auth Required', 401, {'WWW-Authenticate': 'Basic realm="Login"'})

@app.route('/')
def dashboard():
    auth = request.authorization
    if not auth or not check_auth(auth.username, auth.password):
        return authenticate()

    # 1. Get Media Files
    media_items = []
    if os.path.exists(MEDIA_FOLDER):
        video_files = [f for f in os.listdir(MEDIA_FOLDER) if f.lower().endswith(('.mp4', '.mkv', '.mov'))]
        for vid in video_files:
            thumb_name = f"{vid}.jpg"
            generate_thumbnail(os.path.join(MEDIA_FOLDER, vid), thumb_name)
            media_items.append({"name": vid, "thumb": f"thumbnails/{thumb_name}"})

    # 2. Get Watch History from DB
    history = get_recent_history()

    # 3. Get System Stats
    stats = {
        "cpu": psutil.cpu_percent(),
        "ram": psutil.virtual_memory().percent,
        "uptime": datetime.now().strftime("%H:%M:%S")
    }

    return render_template('index.html', items=media_items, stats=stats, history=history)

@app.route('/stream/<filename>')
def stream_file(filename):
    auth = request.authorization
    if not auth or not check_auth(auth.username, auth.password):
        return authenticate()
    
    # ROOT CAUSE: Before we start the stream, log the event!
    log_watch_event(filename)
    
    return send_from_directory(MEDIA_FOLDER, filename)

if __name__ == '__main__':
    init_db() # Create the database on startup
    app.run(host='0.0.0.0', port=5000, debug=True)