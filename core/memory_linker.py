# Filename: core/memory_linker.py

from datetime import datetime

class MemoryLinker:
    def __init__(self, neo4j_connector):
        self.db = neo4j_connector


    def detect_cycles(self):
        query = """
        MATCH path = (m:Memory)-[:RELATED_TO*]->(m)
        WHERE length(path) > 0
        RETURN nodes(path) AS cycle, length(path) AS length
        """
        return self.db.run_query(query)

    def link_memories(self):
        query = """
        MATCH (m1:Memory), (m2:Memory)
        WHERE m1.text <> m2.text
        AND algo.similarity.cosine(m1.vector, m2.vector) > 0.7
        WITH m1, m2
        MATCH path = (m1)-[:RELATED_TO*]->(m2)
        WHERE length(path) > 0
        MERGE (m1)-[r:RELATED_TO]->(m2)
        ON CREATE SET r.weight = 1, r.created_at = datetime()
        ON MATCH SET r.weight = r.weight + CASE WHEN length(path) > 1 THEN 0.5 ELSE 1 END
        RETURN m1.text, m2.text, r.weight, length(path) AS cycle_length
        """
        result = self.db.run_query(query)
        return result

    def link_memories_by_emotion(self):
        query = """
        MATCH (m1:Memory), (m2:Memory)
        WHERE m1.emotion = m2.emotion AND m1.text <> m2.text
        MERGE (m1)-[r:SHARES_EMOTION]->(m2)
        ON CREATE SET r.weight = 1, r.created_at = datetime()
        ON MATCH SET r.weight = r.weight + 1
        RETURN m1.text, m2.text, m1.emotion, r.weight
        """
        return self.db.run_query(query)

    def adjust_memory_weight_and_link(self, memory_text, adjustment):
        result = self.adjust_memory_weight(memory_text, adjustment)
        if adjustment > 0:  # Only link if the memory is being reinforced
            self.link_memories()
            self.link_memories_by_emotion()  # Assuming you added this method
        return result

    def schedule_periodic_tasks(self):
        # Pseudo-code for scheduling
        # schedule.every(1).day.at("00:00").do(self.run_periodic_linking)
        # schedule.every(1).hour.do(self.detect_cycles)
        pass