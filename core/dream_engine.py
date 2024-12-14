# Dream Engine for Maia AI - Symbolic Dream Generation

import random
from datetime import datetime
from backend.neo4j_connection import Neo4jConnection

db = Neo4jConnection(
    uri="neo4j+s://46dc0ffd.databases.neo4j.io:7687",
    user="neo4j",
    password="4KjyYMe6ovQnU9QaRDnwP1q85Ok_rtB9l5p2yiWLgh8"
)

SYMBOLIC_LIBRARY = {
    "joy": "a bright rising sun",
    "sadness": "a wilting flower",
    "anger": "a raging storm",
    "fear": "shadows in the forest",
    "hope": "a distant guiding star",
    "love": "a warm glowing flame",
    "loss": "vanishing stars in the sky",
    "understanding": "a bridge over turbulent waters",
}

def generate_dream():
    query = """
    MATCH (m:Memory)
    RETURN m.event AS event, m.content AS content, m.emotion AS emotion
    ORDER BY rand()
    LIMIT 1
    """
    result = db.query(query)

    if result:
        memory = result[0]
        symbol = SYMBOLIC_LIBRARY.get(memory["emotion"], "a mysterious path")
        dream_description = (
            f"In your dream, you encounter {symbol}. "
            f"The memory of '{memory['content']}' echoes in your mind, "
            f"shaping the surreal landscape around you."
        )
        store_dream(memory["event"], dream_description, memory["emotion"])
        return dream_description
    return "No dreams could be formed."

def store_dream(event, description, emotion):
    query = """
    CREATE (d:Dream {event: $event, description: $description, emotion: $emotion, timestamp: $timestamp})
    """
    parameters = {
        "event": event,
        "description": description,
        "emotion": emotion,
        "timestamp": datetime.now().isoformat()
    }
    db.query(query, parameters)

# Test (Optional)
if __name__ == "__main__":
    print(generate_dream())