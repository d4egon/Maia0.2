
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

# --- Reflexive Introspection Functions ---

def generate_self_query():
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT event, content, emotion, intensity, timestamp 
        FROM memories 
        ORDER BY RANDOM() 
        LIMIT 1
    """")
    memory = cursor.fetchone()
    if memory:
        event = memory["event"]
        content = memory["content"]
        emotion = memory["emotion"]
        intensity = memory["intensity"]
        question = f"What did I learn from {event}, where I felt {emotion} with intensity {intensity:.2f}?"
        logging.info(f"Generated self-query: {question}")
        return question
    conn.close()
    return "No memories found for reflection."

def create_introspective_journal():
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT event, content, emotion, intensity, timestamp 
        FROM memories 
        ORDER BY RANDOM() 
        LIMIT 1
    """")
    memory = cursor.fetchone()
    if memory:
        event = memory["event"]
        content = memory["content"]
        emotion = memory["emotion"]
        intensity = memory["intensity"]
        reflection_log = (f"Today, I reflected on '{event}'. "
                          f"It made me feel {emotion} with intensity {intensity:.2f}. "
                          f"Memory details: {content}.")
        cursor.execute("""
            INSERT INTO memories (event, content, emotion, intensity) 
            VALUES (?, ?, ?, ?)
        """, ("introspection_journal", reflection_log, emotion, 0.9))
        logging.info(f"Created introspective journal entry: {reflection_log}.")
    conn.commit()
    conn.close()

def generate_insight():
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT content, emotion, intensity 
        FROM memories 
        ORDER BY RANDOM() 
        LIMIT 2
    """")
    memories = cursor.fetchall()
    if len(memories) == 2:
        memory1 = memories[0]
        memory2 = memories[1]
        insight = (f"Reflecting on these two experiences: '{memory1['content']}' (emotion: {memory1['emotion']} "
                   f"with intensity {memory1['intensity']:.2f}) and '{memory2['content']}' "
                   f"(emotion: {memory2['emotion']} with intensity {memory2['intensity']:.2f}), "
                   f"I see how emotions shape my reactions.")
        cursor.execute("""
            INSERT INTO memories (event, content, emotion, intensity) 
            VALUES (?, ?, ?, ?)
        """, ("generated_insight", insight, "reflective", 0.85))
        logging.info(f"Generated insight: {insight}.")
    conn.commit()
    conn.close()
