# Filename: core/memory_linker.py

from datetime import datetime
import logging
from typing import List, Dict, Optional
import numpy as np  # For numpy operations if needed

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class MemoryLinker:
    def __init__(self, neo4j_connector):
        """
        Initialize the MemoryLinker with a Neo4j database connector.

        :param neo4j_connector: An instance of Neo4jConnector for database operations.
        """
        self.db = neo4j_connector

    def detect_cycles(self) -> List[Dict]:
        """
        Detect cycles in the memory graph.

        :return: List of dictionaries containing detected cycles and their lengths.
        """
        query = """
        MATCH path = (m:Memory)-[:RELATED_TO*]->(m)
        WHERE length(path) > 0
        RETURN nodes(path) AS cycle, length(path) AS length
        """
        try:
            result = self.db.run_query(query)
            logger.info(f"[CYCLE DETECTION] Detected {len(result)} memory cycles.")
            return result
        except Exception as e:
            logger.error(f"[CYCLE DETECTION ERROR] {e}", exc_info=True)
            return []

    def link_memories(self) -> List[Dict]:
        """
        Link memories based on text similarity and existing relationships.

        :return: List of dictionaries with details of the linked memories.
        """
        query = """
        MATCH (m1:Memory), (m2:Memory)
        WHERE m1.text <> m2.text
        AND gds.alpha.similarity.cosine(m1.vector, m2.vector) > 0.7
        WITH m1, m2
        MATCH path = (m1)-[:RELATED_TO*]->(m2)
        WHERE length(path) > 0
        MERGE (m1)-[r:RELATED_TO]->(m2)
        ON CREATE SET r.weight = 1, r.created_at = datetime()
        ON MATCH SET r.weight = r.weight + CASE WHEN length(path) > 1 THEN 0.5 ELSE 1 END
        RETURN m1.text, m2.text, r.weight, length(path) AS cycle_length
        """
        try:
            result = self.db.run_query(query)
            logger.info(f"[MEMORY LINKING] Linked {len(result)} memory pairs.")
            return result
        except Exception as e:
            logger.error(f"[MEMORY LINKING ERROR] {e}", exc_info=True)
            return []

    def link_memories_by_emotion(self) -> List[Dict]:
        """
        Link memories that share the same emotion.

        :return: List of dictionaries with details of the linked memories by emotion.
        """
        query = """
        MATCH (m1:Memory), (m2:Memory)
        WHERE m1.emotion = m2.emotion AND m1.text <> m2.text
        MERGE (m1)-[r:SHARES_EMOTION]->(m2)
        ON CREATE SET r.weight = 1, r.created_at = datetime()
        ON MATCH SET r.weight = r.weight + 1
        RETURN m1.text, m2.text, m1.emotion, r.weight
        """
        try:
            result = self.db.run_query(query)
            logger.info(f"[EMOTION LINKING] Linked {len(result)} memory pairs by emotion.")
            return result
        except Exception as e:
            logger.error(f"[EMOTION LINKING ERROR] {e}", exc_info=True)
            return []

    def adjust_memory_weight_and_link(self, memory_text: str, adjustment: float) -> List[Dict]:
        """
        Adjust the weight of a memory and link associated memories if the adjustment is positive.

        :param memory_text: Text of the memory to adjust.
        :param adjustment: Float value to adjust the weight by.
        :return: Result of the weight adjustment.
        """
        try:
            result = self.adjust_memory_weight(memory_text, adjustment)
            if adjustment > 0:
                self.link_memories()
                self.link_memories_by_emotion()
            return result
        except Exception as e:
            logger.error(f"[ADJUST WEIGHT ERROR] {e}", exc_info=True)
            return []

    def adjust_memory_weight(self, memory_text: str, adjustment: float) -> List[Dict]:
        """
        Adjust the weight of a memory node.

        :param memory_text: Text of the memory to adjust.
        :param adjustment: Float value to adjust the weight by.
        :return: Result of the weight adjustment query.
        """
        query = f"""
        MATCH (m:Memory {{text: '{memory_text}'}})
        SET m.weight = CASE WHEN EXISTS(m.weight) THEN m.weight + {adjustment} ELSE {adjustment} END
        RETURN m.text, m.weight
        """
        try:
            result = self.db.run_query(query)
            logger.info(f"[WEIGHT ADJUSTMENT] Adjusted weight for memory: {memory_text}")
            return result
        except Exception as e:
            logger.error(f"[WEIGHT ADJUSTMENT ERROR] {e}", exc_info=True)
            return []

    def schedule_periodic_tasks(self):
        """
        Schedule periodic tasks like memory linking and cycle detection.
        This method is left as a placeholder for actual scheduling logic.
        """
        # Pseudo-code for scheduling, to be implemented with actual scheduling library
        # import schedule
        # schedule.every(1).day.at("00:00").do(self.run_periodic_linking)
        # schedule.every(1).hour.do(self.detect_cycles)
        logger.info("[SCHEDULER] Periodic tasks scheduling would be implemented here.")

    def recursive_linking(self, start_node_id: str, depth: int = 3):
        """
        Recursively link nodes based on themes and emotions.
    
        :param start_node_id: Starting node ID.
        :param depth: Depth of recursion.
        """
        if depth <= 0:
            return
        try:
            query = f"""
            MATCH (n:Memory {{id: '{start_node_id}'}})-[:RELATED_TO|:SHARES_EMOTION]->(related:Memory)
            WITH related LIMIT 10
            MERGE (n)-[:REINFORCES {{weight: 0.5}}]->(related)
            WITH related
            CALL {{ 
                WITH related
                MATCH (related)-[:RELATED_TO|:SHARES_EMOTION]->(next:Memory)
                WHERE NOT (n)-[:REINFORCES]->(next)
                WITH next LIMIT 10
                MERGE (related)-[:REINFORCES {{weight: 0.5}}]->(next)
            }}
            """
            self.db.run_query(query)
            # Recursive call on all newly linked memories
            for memory in self.db.run_query(f"MATCH (m:Memory {{id: '{start_node_id}'}})-[:REINFORCES]->(related) RETURN related.id"):
                self.recursive_linking(memory['id'], depth - 1)
            logger.info(f"[RECURSIVE LINKING] Linked recursively for node {start_node_id}.")
        except Exception as e:
            logger.error(f"[RECURSIVE LINKING ERROR] {e}", exc_info=True)

    def visualize_thought_process(self, start_node_id: str) -> Optional[Dict]:
        """
        Generate a visualization of the thought process based on memory links.

        :param start_node_id: Starting node ID for the visualization.
        :return: A dictionary representing the visualized graph or None if an error occurs.
        """
        try:
            # This is a simplified version; for actual visualization, you'd need to use a graph visualization library
            query = f"""
            MATCH path = (m:Memory {{id: '{start_node_id}'}})-[:RELATED_TO|:SHARES_EMOTION|:REINFORCES*1..3]->(other)
            RETURN path
            """
            paths = self.db.run_query(query)
            # Here, we simulate visualization by returning paths; in practice, you'd process this for graph rendering
            logger.info(f"[VISUALIZATION] Generated thought process visualization for node {start_node_id}")
            return {"paths": [str(path) for path in paths]}
        except Exception as e:
            logger.error(f"[VISUALIZATION ERROR] {e}", exc_info=True)
            return None

    def consolidate_memories(self):
        """
        Consolidate similar memories by merging or strengthening connections.
        """
        try:
            query = """
            MATCH (m1:Memory)-[r:RELATED_TO]->(m2:Memory)
            WHERE gds.alpha.similarity.cosine(m1.vector, m2.vector) > 0.9
            MERGE (m1)-[c:CONSOLIDATED_WITH]->(m2)
            SET c.weight = CASE WHEN EXISTS(r.weight) THEN r.weight + 1 ELSE 1 END
            WITH m1, m2, c
            DETACH DELETE r  # Remove the old relationship if it exists
            """
            self.db.run_query(query)
            logger.info("[MEMORY CONSOLIDATION] Memories consolidation process completed.")
        except Exception as e:
            logger.error(f"[MEMORY CONSOLIDATION ERROR] {e}", exc_info=True)