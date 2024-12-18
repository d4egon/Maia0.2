# Filename: /neo4j_setup.py

import os
import logging
from core.neo4j_connector import Neo4jConnector
from dotenv import load_dotenv # type: ignore

# Initialize Logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

# Load Environment Variables
load_dotenv()
NEO4J_URI = os.getenv("NEO4J_URI", "neo4j+s://46dc0ffd.databases.neo4j.io:7687")
NEO4J_USER = os.getenv("NEO4J_USER", "neo4j")
NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD", "YOUR_PASSWORD")

# Initialize Neo4j Connection
try:
    neo4j = Neo4jConnector(NEO4J_URI, NEO4J_USER, NEO4J_PASSWORD)
    logger.info("[INIT] Connected to Neo4j successfully.")
except Exception as e:
    logger.critical(f"[ERROR] Failed to connect to Neo4j: {e}", exc_info=True)
    exit(1)

# Define Triggers
triggers = [
    {
        "name": "LinkMemoriesOnCreate",
        "query": """
        MATCH (m:Memory)
        WHERE NOT (m)-[:RELATED_TO]->()
        WITH m
        MATCH (other:Memory)
        WHERE m.text <> other.text
        AND algo.similarity.cosine(m.vector, other.vector) > 0.7
        MERGE (m)-[r:RELATED_TO]->(other)
        SET r.weight = coalesce(r.weight, 0) + 1
        """
    },
    {
        "name": "UpdateEmotionState",
        "query": """
        MATCH (m:Memory)-[:HAS_EMOTION]->(e:Emotion)
        WHERE e.intensity <> m.emotional_state
        SET e.intensity = m.emotional_state
        """
    }
]

# Create Triggers
for trigger in triggers:
    try:
        existing_triggers = [t['name'] for t in neo4j.list_triggers()]
        if trigger['name'] in existing_triggers:
            logger.info(f"[SKIP] Trigger '{trigger['name']}' already exists.")
        else:
            neo4j.create_trigger(trigger['name'], trigger['query'])
            logger.info(f"[SUCCESS] Trigger '{trigger['name']}' created successfully.")
    except Exception as e:
        logger.error(f"[ERROR] Failed to create trigger '{trigger['name']}': {e}", exc_info=True)

# Verify Active Triggers
try:
    active_triggers = neo4j.list_triggers()
    logger.info("[VERIFY] Active Triggers:")
    for trigger in active_triggers:
        logger.info(f" - {trigger['name']}")
except Exception as e:
    logger.error(f"[ERROR] Failed to list active triggers: {e}", exc_info=True)

# Close Neo4j Connection
neo4j.close()
logger.info("[SHUTDOWN] Neo4j connection closed.")
