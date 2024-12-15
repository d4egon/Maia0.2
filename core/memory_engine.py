# Filename: /core/memory_engine.py

import logging
from datetime import datetime
from functools import lru_cache

# Set up logging
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

class MemoryEngine:
    DECAY_FACTOR = 0.1
    CACHE_SIZE = 128

    def __init__(self, db):
        self.db = db
        self.memory_cache = {}

    @lru_cache(maxsize=CACHE_SIZE)
    def search_memory(self, text):
        """
        Search memory using an in-memory cache for fast lookups.
        Falls back to Neo4j if not found.
        """
        if text in self.memory_cache:
            logger.debug(f"[CACHE HIT] Found in memory cache: {text}")
            return self.memory_cache[text]

        query = """
        MATCH (m:Memory {text: $text})
        RETURN m.emotion, m.weight, m.last_updated
        """
        result = self.db.run_query(query, {"text": text.lower()})
        if result:
            self.memory_cache[text] = result[0]
            logger.info(f"[CACHE STORE] Stored in cache: {text}")
            return result[0]
        
        logger.warning(f"[SEARCH MISS] No memory found for: {text}")
        return None

    def store_memory(self, text, emotion, additional_data=None):
        """
        Store memory with advanced transaction management.
        """
        timestamp = datetime.now().isoformat()

        with self.db.transaction() as tx:
            try:
                # Store Memory Node
                query = """
                MERGE (m:Memory {text: $text})
                ON CREATE SET m.created_at = $timestamp, m.weight = 1
                ON MATCH SET m.last_updated = $timestamp, m.emotion = $emotion
                """
                tx.run(query, {
                    "text": text.lower(),
                    "emotion": emotion.lower(),
                    "timestamp": timestamp
                })

                self.link_emotion(tx, text, emotion)

                if additional_data:
                    self.add_additional_data(tx, text, additional_data)

                tx.commit()
                logger.info(f"[MEMORY STORED] '{text}' | Emotion: '{emotion}'")
            except Exception as e:
                logger.error(f"[STORE FAILED] Memory storage failed: {e}", exc_info=True)
                tx.rollback()

    def link_emotion(self, tx, text, emotion):
        """
        Create or update an emotion link using a transactional query.
        """
        query = """
        MERGE (e:Emotion {type: $emotion})
        MERGE (m:Memory {text: $text})
        MERGE (m)-[:LINKED_TO]->(e)
        """
        tx.run(query, {"text": text.lower(), "emotion": emotion.lower()})
        logger.info(f"[LINK EMOTION] Linked '{emotion}' to '{text}'")

    def add_additional_data(self, tx, text, additional_data):
        """
        Update memory node with additional contextual data.
        """
        try:
            updates = ", ".join([f"m.{key} = ${key}" for key in additional_data.keys()])
            query = f"""
            MATCH (m:Memory {{text: $text}})
            SET {updates}
            """
            parameters = {"text": text.lower(), **additional_data}
            tx.run(query, parameters)
            logger.info(f"[DATA ADDED] Updated '{text}' with additional data.")
        except Exception as e:
            logger.error(f"[DATA FAILED] Additional data update failed: {e}", exc_info=True)

    def apply_memory_decay(self, decay_factor=DECAY_FACTOR):
        """
        Batch memory decay operation using `UNWIND`.
        """
        try:
            query = """
            MATCH (m:Memory)
            WHERE m.weight > 0
            WITH m, m.weight - $decay_factor AS new_weight
            SET m.weight = CASE 
                            WHEN new_weight < 0 THEN 0 
                            ELSE new_weight 
                          END
            """
            self.db.run_query(query, {"decay_factor": decay_factor})
            logger.info(f"[DECAY APPLIED] Memory decay factor applied: {decay_factor}")
        except Exception as e:
            logger.error(f"[DECAY FAILED] Memory decay failed: {e}", exc_info=True)

    def adjust_memory_weight(self, text, adjustment):
        """
        Dynamically adjust memory weight.
        """
        try:
            query = """
            MATCH (m:Memory {text: $text})
            SET m.weight = COALESCE(m.weight, 0) + $adjustment
            """
            self.db.run_query(query, {"text": text.lower(), "adjustment": adjustment})
            logger.info(f"[WEIGHT ADJUSTED] '{text}' adjusted by {adjustment}")
        except Exception as e:
            logger.error(f"[ADJUST FAILED] Weight adjustment failed: {e}", exc_info=True)