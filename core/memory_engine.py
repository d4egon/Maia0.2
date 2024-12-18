
import logging
from datetime import datetime
from functools import lru_cache

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
        if text in self.memory_cache:
            logger.debug(f"[CACHE HIT] Found in memory cache: {text}")
            return self.memory_cache[text]

        query = """
            CALL db.index.fulltext.queryNodes('memoryIndex', $text)
            YIELD node, score
            WHERE score > 0.7
            RETURN node.text AS text, node.emotion AS emotion, node.weight AS weight, node.last_updated AS last_updated
            ORDER BY score DESC LIMIT 1
            """
        result = self.db.run_query(query, {"text": text.lower()})
        if result:
            self.memory_cache[text] = result[0]
            logger.info(f"[CACHE STORE] Stored in cache: {text}")
            return result[0]

        logger.warning(f"[SEARCH MISS] No memory found for: {text}")
        return None

    def store_memory(self, text, emotion, additional_data=None):
        timestamp = datetime.now().isoformat()
        try:
            query = """
                MERGE (m:Memory {text: $text})
                ON CREATE SET m.created_at = $timestamp, m.weight = 1
                ON MATCH SET m.last_updated = $timestamp, m.emotion = $emotion
                """
            self.db.run_query(query, {
                "text": text.lower(),
                "emotion": emotion.lower(),
                "timestamp": timestamp
            })
            logger.info(f"[MEMORY STORED] '{text}' | Emotion: '{emotion}'")
        except Exception as e:
            logger.error(f"[STORE FAILED] Memory storage failed: {e}", exc_info=True)