# Filename: core/memory_linker.py

from datetime import datetime
import logging
from typing import List, Dict

# Configure logging
logging.basicConfig(level=logging.INFO)
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
            logger.info(f"Detected {len(result)} memory cycles.")
            return result
        except Exception as e:
            logger.error(f"Error detecting cycles: {e}")
            raise

    def link_memories(self) -> List[Dict]:
        """
        Link memories based on text similarity and existing relationships.

        :return: List of dictionaries with details of the linked memories.
        """
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
        try:
            result = self.db.run_query(query)
            logger.info(f"Linked {len(result)} memory pairs.")
            return result
        except Exception as e:
            logger.error(f"Error linking memories: {e}")
            raise

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
            logger.info(f"Linked {len(result)} memory pairs by emotion.")
            return result
        except Exception as e:
            logger.error(f"Error linking memories by emotion: {e}")
            raise

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
            logger.error(f"Error adjusting memory weight and linking: {e}")
            raise

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
            logger.info(f"Adjusted weight for memory: {memory_text}")
            return result
        except Exception as e:
            logger.error(f"Error adjusting memory weight: {e}")
            raise

    def schedule_periodic_tasks(self):
        """
        Schedule periodic tasks like memory linking and cycle detection.
        This method is left as a placeholder for actual scheduling logic.
        """
        # Pseudo-code for scheduling, to be implemented with actual scheduling library
        # schedule.every(1).day.at("00:00").do(self.run_periodic_linking)
        # schedule.every(1).hour.do(self.detect_cycles)
        logger.info("Periodic tasks scheduling would be implemented here.")