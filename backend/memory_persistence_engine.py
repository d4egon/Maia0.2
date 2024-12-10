# memory_persistence_engine.py - Memory Persistence for MAIA

# Import SQLite and Neo4j
import sqlite3
from backend.neo4j_connection import neo4j_db

# Database Paths
SQLITE_DB_PATH = "data/maia_emotion_db.db"

# --- SQLite Memory Storage ---
def connect_sqlite_db():
    conn = sqlite3.connect(SQLITE_DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

# Store Memory in SQLite
def store_memory_sqlite(event, content, emotion, intensity):
    conn = connect_sqlite_db()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO memories (event, content, emotion, intensity, timestamp) 
        VALUES (?, ?, ?, ?, CURRENT_TIMESTAMP)
    """, (event, content, emotion, intensity))
    conn.commit()
    conn.close()
    return {"message": "Memory stored in SQLite!"}

# Retrieve Memories from SQLite
def retrieve_memories_sqlite(emotion, limit=5):
    conn = connect_sqlite_db()
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
    return [{"content": row["content"], "intensity": row["intensity"], "timestamp": row["timestamp"]} for row in memories]


# --- Neo4j Memory Storage ---
def store_memory_neo4j(event, content, emotion, intensity):
    query = """
    MERGE (m:Memory {content: $content, emotion: $emotion})
    ON CREATE SET m.intensity = $intensity, m.event = $event, m.timestamp = timestamp()
    ON MATCH SET m.intensity = m.intensity + $intensity
    RETURN m
    """
    params = {
        "content": content,
        "emotion": emotion,
        "intensity": intensity,
        "event": event,
    }
    result = neo4j_db.run_query(query, params)
    return {"message": "Memory stored in Neo4j!", "result": result}

# Retrieve Memories from Neo4j
def retrieve_memories_neo4j(emotion, limit=5):
    query = """
    MATCH (m:Memory {emotion: $emotion})
    RETURN m.content AS content, m.intensity AS intensity, m.timestamp AS timestamp
    ORDER BY m.intensity DESC, m.timestamp DESC
    LIMIT $limit
    """
    params = {"emotion": emotion, "limit": limit}
    result = neo4j_db.run_query(query, params)
    return result


# --- Combined Storage Function (Flexible Mode) ---
def store_memory(event, content, emotion, intensity, use_neo4j=False):
    if use_neo4j:
        return store_memory_neo4j(event, content, emotion, intensity)
    else:
        return store_memory_sqlite(event, content, emotion, intensity)


def retrieve_memories(emotion, limit=5, use_neo4j=False):
    if use_neo4j:
        return retrieve_memories_neo4j(emotion, limit)
    else:
        return retrieve_memories_sqlite(emotion, limit)
