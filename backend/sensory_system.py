
# --- Import Required Libraries ---
import logging
import sqlite3
import random

# --- Logging Setup ---
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# --- Database Setup ---
DB_PATH = "maia_emotion_db.db"

def connect_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

# --- Virtual Sensory System ---

SENSORY_INPUT_MAP = {
    "light": {"low": "calm", "medium": "alert", "high": "excited"},
    "sound": {"low": "peaceful", "medium": "focused", "high": "overwhelmed"},
    "vibration": {"low": "stable", "medium": "aware", "high": "startled"}
}

def process_sensory_input(sensor_type, intensity_level):
    if sensor_type not in SENSORY_INPUT_MAP:
        logging.warning(f"Unknown sensory input: {sensor_type}")
        return "neutral"
    emotion = SENSORY_INPUT_MAP[sensor_type].get(intensity_level, "neutral")
    logging.info(f"Sensory input processed: {sensor_type} -> {intensity_level} -> {emotion}")
    conn = connect_db()
    cursor = conn.cursor()
    description = f"Sensed {sensor_type} at {intensity_level} intensity, felt {emotion}."
    cursor.execute("""
        INSERT INTO memories (event, content, emotion, intensity) 
        VALUES (?, ?, ?, ?)
    """, ("sensory_input", description, emotion, random.uniform(0.5, 0.9)))
    conn.commit()
    conn.close()
    return emotion

def simulate_sensory_stream():
    sensors = ["light", "sound", "vibration"]
    intensity_levels = ["low", "medium", "high"]
    for _ in range(5):
        sensor_type = random.choice(sensors)
        intensity_level = random.choice(intensity_levels)
        process_sensory_input(sensor_type, intensity_level)
