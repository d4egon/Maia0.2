# Emotional Web Prototype (Neo4j Enhancements)
# -------------------------------------------
# Roadmap Pointer:
# 1. Create a Neo4j database with nodes: Emotion, Memory, Event, Concept, Sensory Input
# 2. Define edges: Intensity, Relevance, Context, Memory Trace
# 3. Implement memory imprint creation with emotional weights
# 4. Add a decay function for unused memories
# 5. Simulate triggered responses with cascading node activation

from neo4j import GraphDatabase

class EmotionalWeb:
    def __init__(self, uri, user, password):
        self.driver = GraphDatabase.driver(uri, auth=(user, password))

    def close(self):
        self.driver.close()

    def create_node(self, label, properties):
        with self.driver.session() as session:
            query = f"CREATE (n:{label} {{ {', '.join([f'{k}: ${k}' for k in properties.keys()])} }})"
            session.run(query, **properties)

    def create_relationship(self, from_label, from_name, to_label, to_name, relation, properties):
        with self.driver.session() as session:
            query = (
                f"MATCH (a:{from_label} {{name: $from_name}}), "
                f"(b:{to_label} {{name: $to_name}}) "
                f"CREATE (a)-[r:{relation} {{ {', '.join([f'{k}: ${k}' for k in properties.keys()])} }}]->(b)"
            )
            session.run(query, from_name=from_name, to_name=to_name, **properties)

    def query_memory(self, label, memory_name):
        with self.driver.session() as session:
            result = session.run(
                f"MATCH (n:{label} {{name: $memory_name}}) RETURN n",
                memory_name=memory_name
            )
            return [record["n"] for record in result]

# Example Usage (Commented Out)
# web = EmotionalWeb("bolt://localhost:7687", "neo4j", "password")
# web.create_node("Emotion", {"name": "Joy", "intensity": 0.9, "context": "positive"})
# web.create_node("Memory", {"name": "First Win", "event": "Achieved goal", "intensity": 0.7})
# web.create_relationship("Emotion", "Joy", "Memory", "First Win", "CONNECTED_TO", {"relevance": 0.8})
# memories = web.query_memory("Memory", "First Win")
# print(memories)
# web.close()