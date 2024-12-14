# neo4j_setup.py - Improved Database Setup for Neo4j

from backend.neo4j_connection import Neo4jConnection

# Initialize Neo4j
db = Neo4jConnection(
    uri="neo4j+s://46dc0ffd.databases.neo4j.io:7687",
    user="neo4j",
    password="4KjyYMe6ovQnU9QaRDnwP1q85Ok_rtB9l5p2yiWLgh8"
)

# Corrected Constraints Setup
setup_queries = [
    """
    CREATE CONSTRAINT IF NOT EXISTS FOR (e:Emotion)
    REQUIRE e.name IS UNIQUE
    """,
    """
    CREATE CONSTRAINT IF NOT EXISTS FOR (m:Memory)
    REQUIRE m.event IS UNIQUE
    """,
    """
    CREATE CONSTRAINT IF NOT EXISTS FOR (j:JournalEntry)
    REQUIRE j.title IS UNIQUE
    """
]

# Define Data Initialization Queries
label_creation_queries = [
    """
    MERGE (j:JournalEntry {title: "Initial Journal Entry"})
    ON CREATE SET j.content = "Maia's journal system initialized.",
                  j.emotional_state = "neutral",
                  j.timestamp = datetime()
    """,
    """
    MERGE (e:Emotion {name: "neutral"})
    ON CREATE SET e.intensity = 0.5, e.context = "system initialization"
    """,
    """
    MERGE (e:Emotion {name: "happy"})
    ON CREATE SET e.intensity = 0.8, e.context = "positive interaction"
    """,
    """
    MERGE (e:Emotion {name: "agreement"})
    ON CREATE SET e.intensity = 1.0, e.context = "affirmation"
    """,
    """
    MERGE (e:Emotion {name: "disagreement"})
    ON CREATE SET e.intensity = 1.0, e.context = "negation"
    """
]

# Execute Setup Queries
try:
    for query in setup_queries:
        db.query(query)
    print("Database constraints created successfully.")

    for query in label_creation_queries:
        db.query(query)
    print("Database setup complete. All initial labels created.")
except Exception as e:
    print(f"Error occurred: {e}")

db.close()