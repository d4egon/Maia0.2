# Filename: core/memory_linker.py

from datetime import datetime

class MemoryLinker:
    def __init__(self, neo4j_connector):
        self.db = neo4j_connector

    def link_memories(self):
        """
        Automatically links memories based on content similarity.
        """
        query = """
        MATCH (m1:Memory), (m2:Memory)
        WHERE m1.text <> m2.text
        AND algo.similarity.cosine(m1.vector, m2.vector) > 0.7
        MERGE (m1)-[r:RELATED_TO]->(m2)
        ON CREATE SET r.weight = 1, r.created_at = datetime()
        ON MATCH SET r.weight = r.weight + 1
        RETURN m1.text, m2.text, r.weight
        """
        result = self.db.run_query(query)
        return result

    def adjust_memory_weight(self, memory_text, adjustment):
        """
        Adjusts memory weight based on user feedback.
        """
        query = """
        MATCH (m:Memory {text: $memory_text})
        SET m.weight = coalesce(m.weight, 0) + $adjustment
        RETURN m.text, m.weight
        """
        result = self.db.run_query(query, {"memory_text": memory_text.lower(), "adjustment": adjustment})
        return result

    def run_periodic_linking(self):
        """
        Triggers memory linking periodically.
        """
        result = self.link_memories()
        print(f"[Memory Linking Completed] {len(result)} relationships created.")