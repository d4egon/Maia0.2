# Filename: /neo4j_setup.py

from core.neo4j_connector import Neo4jConnector

# Initialize Neo4j
neo4j = Neo4jConnector("neo4j+s://46dc0ffd.databases.neo4j.io:7687", "neo4j", "YOUR_PASSWORD")

# Define Triggers
memory_linking_trigger = """
MATCH (m:Memory)
WHERE NOT (m)-[:RELATED_TO]->()
WITH m
MATCH (other:Memory)
WHERE m.text <> other.text
AND algo.similarity.cosine(m.vector, other.vector) > 0.7
MERGE (m)-[r:RELATED_TO]->(other)
SET r.weight = coalesce(r.weight, 0) + 1
"""

emotional_update_trigger = """
MATCH (m:Memory)-[:HAS_EMOTION]->(e:Emotion)
WHERE e.intensity <> m.emotional_state
SET e.intensity = m.emotional_state
"""

# Create Triggers
neo4j.create_trigger("LinkMemoriesOnCreate", memory_linking_trigger)
neo4j.create_trigger("UpdateEmotionState", emotional_update_trigger)

# Verify Triggers
active_triggers = neo4j.list_triggers()
for trigger in active_triggers:
    print(f"Active Trigger: {trigger['name']}")

neo4j.close()