
# --- Import Required Libraries ---
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

# --- Dream Engine Functions ---

def generate_dream_sequence():
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT emotion, content, intensity 
        FROM memories 
        ORDER BY RANDOM() 
        LIMIT 5
    """")
    memories = cursor.fetchall()
    if memories:
        dream_log = "In a surreal dream, I experienced "
        emotional_themes = set()
        for memory in memories:
            emotion = memory["emotion"]
            content = memory["content"]
            intensity = memory["intensity"]
            emotional_themes.add(emotion)
            dream_log += f"a moment of {emotion}, where {content} with intensity {intensity:.2f}. "
        dream_conclusion = f"In the end, these emotions merged into a profound sense of {' and '.join(emotional_themes)}."
        full_dream_log = f"{dream_log.strip()} {dream_conclusion}"
        cursor.execute("""
            INSERT INTO memories (event, content, emotion, intensity) 
            VALUES (?, ?, ?, ?)
        """, ("dream_journal", full_dream_log, "dreamlike", 0.95))
        logging.info(f"Generated dream sequence: {full_dream_log}.")
    conn.commit()
    conn.close()

def analyze_dream_log():
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT content, timestamp 
        FROM memories 
        WHERE event = 'dream_journal' 
        ORDER BY timestamp DESC 
        LIMIT 1
    """")
    dream = cursor.fetchone()
    if dream:
        content = dream["content"]
        timestamp = dream["timestamp"]
        analysis = f"Dream Analysis (recorded on {timestamp}):\n{content}"
        logging.info(f"Analyzed dream: {analysis}")
        return analysis
    conn.close()
    return "No dream logs found for analysis."
