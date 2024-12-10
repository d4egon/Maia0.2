
# --- Import Required Libraries ---
import os
import sqlite3
import random
import logging
import threading
import time
from datetime import datetime
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import psutil

# --- Logging Setup ---
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# --- Flask App Setup ---
app = Flask(__name__, template_folder="templates", static_folder="static")
CORS(app)

# --- Database Setup ---
DB_PATH = "maia_emotion_db.db"

def connect_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

# --- Initialize Database ---
def initialize_database():
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS connections (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            keyword TEXT NOT NULL,
            emotion TEXT NOT NULL,
            color TEXT NOT NULL,
            pleasure REAL DEFAULT 0.5,
            arousal REAL DEFAULT 0.5,
            weight REAL DEFAULT 1.0
        );
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS memories (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            event TEXT NOT NULL,
            content TEXT NOT NULL,
            emotion TEXT NOT NULL,
            intensity REAL NOT NULL,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        );
    """)
    conn.commit()
    conn.close()
    logging.info("Database initialized with 'connections' and 'memories' tables.")

initialize_database()

# --- Background Task Functions ---
def consolidate_memories():
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT emotion, AVG(intensity) as avg_intensity, COUNT(*) as count 
        FROM memories 
        GROUP BY emotion 
        HAVING count > 1
    """)
    for row in cursor.fetchall():
        emotion = row["emotion"]
        avg_intensity = row["avg_intensity"]
        count = row["count"]
        cursor.execute("""
            DELETE FROM memories WHERE emotion = ?
        """, (emotion,))
        cursor.execute("""
            INSERT INTO memories (event, content, emotion, intensity) 
            VALUES (?, ?, ?, ?)
        """, ("memory_consolidation", f"Consolidated {count} memories.", emotion, avg_intensity))
        conn.commit()
        logging.info(f"Consolidated {count} memories of emotion: {emotion}.")
    conn.close()

def resource_monitor():
    while True:
        cpu_usage = psutil.cpu_percent(interval=1)
        ram_usage = psutil.virtual_memory().percent
        if cpu_usage < 50 and ram_usage < 60:
            logging.info(f"System resources optimal (CPU: {cpu_usage}%, RAM: {ram_usage}%). Running memory consolidation.")
            consolidate_memories()
        else:
            logging.info(f"High resource usage detected (CPU: {cpu_usage}%, RAM: {ram_usage}%). Skipping tasks.")
        time.sleep(60)  # Run every 60 seconds

# --- Start Background Thread ---
background_thread = threading.Thread(target=resource_monitor, daemon=True)
background_thread.start()
