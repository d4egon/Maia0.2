
# Merged Emotion Engine for Maia AI

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
import numpy as np

# --- Logging Setup ---
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# --- Flask App Setup ---
app = Flask(__name__, template_folder="templates", static_folder="static")
CORS(app)

# --- Database Setup ---
DB_PATH = "C:/Maia/Maia0.2/data/maia_emotion_db.db"

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

# --- Memory Management ---
def store_memory(event_type, content, emotion, intensity):
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO memories (event, content, emotion, intensity) 
        VALUES (?, ?, ?, ?)
    """, (event_type, content, emotion, intensity))
    conn.commit()
    conn.close()
    logging.info(f"Memory stored: {event_type}, {content}, {emotion}, {intensity}")

def retrieve_memories(emotion, limit=5):
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT content, intensity, timestamp 
        FROM memories 
        WHERE emotion = ? 
        ORDER BY intensity DESC, timestamp DESC 
        LIMIT ?
    """, (emotion, limit))
    memories = cursor.fetchall()
    conn.close()
    return memories

# --- Emotion Engine Functions ---
emotion_clusters = {}

def fetch_emotion_clusters():
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM connections")
    clusters = {
        row['color']: {
            "emotion": row['emotion'],
            "pleasure": row['pleasure'],
            "arousal": row['arousal'],
            "weight": row['weight'],
            "keywords": []
        } for row in cursor.fetchall()
    }
    cursor.execute("SELECT keyword, emotion FROM connections")
    for row in cursor.fetchall():
        color = next((c for c, e in clusters.items() if e["emotion"] == row['emotion']), None)
        if color:
            clusters[color]['keywords'].append(row['keyword'])
    conn.close()
    return clusters

emotion_clusters = fetch_emotion_clusters()

# --- Emotional State Tracker ---
emotional_state = {
    "joy": 0.5,
    "sadness": 0.5,
    "anger": 0.5,
    "trust": 0.5,
    "fear": 0.5,
    "anticipation": 0.5,
    "surprise": 0.5,
    "disgust": 0.5
}

def update_emotional_state(emotion, intensity):
    if emotion in emotional_state:
        current_value = emotional_state[emotion]
        emotional_state[emotion] = np.clip(current_value + intensity, 0, 1)
        logging.info(f"Updated emotional state: {emotion} -> {emotional_state[emotion]}")

def apply_emotional_drift():
    drift_rate = 0.01
    for emotion in emotional_state:
        current_value = emotional_state[emotion]
        if current_value > 0.5:
            emotional_state[emotion] = max(0.5, current_value - drift_rate)
        elif current_value < 0.5:
            emotional_state[emotion] = min(0.5, current_value + drift_rate)
    logging.info(f"Applied emotional drift: {emotional_state}")

# --- Advanced Introspective Functions ---
def generate_creative_thought():
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("SELECT content, emotion FROM memories ORDER BY RANDOM() LIMIT 1")
    memory = cursor.fetchone()
    if memory:
        content, emotion = memory["content"], memory["emotion"]
        poems = {
            "joy": f"In the warmth of memory's glow, I found {content}, like dawn's gentle embrace.",
            "sadness": f"A shadow lingers where {content} once stood, fading but never gone.",
            "anger": f"Fiery storms rage where {content} struck deep, yet from the ashes, growth begins.",
            "trust": f"Through uncertain winds, {content} anchored me, steadfast and sure."
        }
        poem = poems.get(emotion, f"From the depths of thought, {content} emerged, undefined yet profound.")
        store_memory("creative_thought", poem, emotion, 0.9)

def advanced_background_task_runner():
    while True:
        generate_creative_thought()
        apply_emotional_drift()
        time.sleep(600)

background_thread = threading.Thread(target=advanced_background_task_runner, daemon=True)
background_thread.start()
