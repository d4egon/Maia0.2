
# --- Import Required Libraries ---
import numpy as np
import logging
import sqlite3

# --- Logging Setup ---
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# --- Database Setup ---
DB_PATH = "maia_emotion_db.db"

def connect_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

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

def get_emotional_state():
    return emotional_state.copy()

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

def generate_blended_emotions():
    blended_emotions = {
        "love": (emotional_state["joy"] + emotional_state["trust"]) / 2,
        "optimism": (emotional_state["joy"] + emotional_state["anticipation"]) / 2,
        "submission": (emotional_state["trust"] + emotional_state["fear"]) / 2,
        "awe": (emotional_state["surprise"] + emotional_state["trust"]) / 2,
        "disappointment": (emotional_state["sadness"] + emotional_state["surprise"]) / 2
    }
    logging.info(f"Generated blended emotions: {blended_emotions}")
    return blended_emotions

def log_emotional_change(emotion, intensity):
    conn = connect_db()
    cursor = conn.cursor()
    description = f"Emotion '{emotion}' changed by {intensity:.2f}."
    cursor.execute("""
        INSERT INTO memories (event, content, emotion, intensity) 
        VALUES (?, ?, ?, ?)
    """, ("emotional_change", description, emotion, intensity))
    conn.commit()
    logging.info(f"Logged emotional change: {description}.")
    conn.close()

def check_emotional_triggers():
    high_emotions = {e: v for e, v in emotional_state.items() if v > 0.75}
    if high_emotions:
        for emotion, intensity in high_emotions.items():
            log_emotional_change(emotion, intensity)
            logging.info(f"Triggered action due to high emotion: {emotion} ({intensity}).")
