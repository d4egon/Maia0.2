
# --- Import Required Libraries ---
import os
import sqlite3
import logging

# --- Logging Setup ---
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# --- Database Setup ---
DB_PATH = "maia_emotion_db.db"

def connect_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

# --- Memory & Persistence Functions ---
def store_memory(event, content, emotion, intensity):
    """ Store a new memory with emotional context. """
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO memories (event, content, emotion, intensity) 
        VALUES (?, ?, ?, ?)
    """, (event, content, emotion, intensity))
    conn.commit()
    logging.info(f"Memory stored: {event}, {content}, {emotion}, {intensity}.")
    conn.close()

def recall_memories_by_emotion(emotion, limit=5):
    """ Retrieve memories based on emotional context. """
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

def search_memories(keyword):
    """ Search for memories based on content keywords. """
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT event, content, emotion, intensity, timestamp 
        FROM memories 
        WHERE content LIKE ? 
        ORDER BY timestamp DESC
    """, (f"%{keyword}%",))
    search_results = cursor.fetchall()
    conn.close()
    return search_results

def update_memory_intensity(memory_id, new_intensity):
    """ Update the intensity of an existing memory. """
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE memories 
        SET intensity = ? 
        WHERE id = ?
    """, (new_intensity, memory_id))
    conn.commit()
    logging.info(f"Updated memory {memory_id} with new intensity {new_intensity}.")
    conn.close()

# --- Example Test Data ---
# Example memory insertion for testing
store_memory("user_interaction", "Discussed emotional processing with AI.", "thoughtful", 0.8)
sample_memories = recall_memories_by_emotion("thoughtful")
search_results = search_memories("processing")
