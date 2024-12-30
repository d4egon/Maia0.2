import logging
from datetime import datetime
from core.neo4j_connector import Neo4jConnector
import emoji
import re
from typing import Dict, List, Any, Optional

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

class MemoryEngine:
    DECAY_FACTOR = 0.1

    def __init__(self, db: Neo4jConnector):
        """
        Initialize MemoryEngine with database connector and setup initial configurations.

        :param db: An instance of Neo4jConnector for database operations.
        """
        self.db = db
        self.memory_cache: Dict[str, Dict] = {}
        self._setup_index()

    def _setup_index(self):
        """Ensure the full-text index and constraint exist in Neo4j."""
        try:
            self.db.run_query(
                "CREATE FULLTEXT INDEX memoryIndex IF NOT EXISTS FOR (n:Memory) ON EACH [n.text]"
            )
            self.db.run_query(
                "CREATE CONSTRAINT IF NOT EXISTS FOR (e:Emotion) REQUIRE e.name IS UNIQUE"
            )
            logger.info("[INDEX SETUP] Full-text index 'memoryIndex' and constraint on Emotion.name created or already exist.")
        except Exception as e:
            logger.error(f"[INDEX SETUP FAILED] {e}", exc_info=True)


    @staticmethod
    def clean_text(text: str) -> str:
        """Convert emojis and sanitize text for Neo4j full-text queries."""
        text_with_emojis = emoji.demojize(text)
        sanitized_text = re.sub(r'[\s"<>|(){}\[\]+]', ' ', text_with_emojis).strip()
        logger.debug(f"[TEXT SANITIZATION] Original: '{text}' | Emojis Converted: '{text_with_emojis}' | Sanitized: '{sanitized_text}'")
        return sanitized_text


    @staticmethod
    def prepare_query_text(text: str) -> str:
        """Wrap query text in quotes to prevent EOF errors."""
        if not text.strip():
            return ""
        wrapped_text = f'"{text}"'
        logger.debug(f"[PREPARED QUERY] Wrapped Text: {wrapped_text}")
        return wrapped_text

    def search_memory(self, text: str) -> Optional[Dict]:
        """Search memory with sanitized text and improved similarity handling."""
        sanitized_text = self.clean_text(text.lower())
    
        if not sanitized_text:
            logger.warning("[EMPTY QUERY] Skipping search for empty sanitized text.")
            return None
    
        if sanitized_text in self.memory_cache:
            logger.info(f"[CACHE HIT] Memory found in cache: {sanitized_text}")
            return self.memory_cache[sanitized_text]
    
        try:
            query = """
            CALL db.index.fulltext.queryNodes('memoryIndex', $text) YIELD node, score
            WHERE score >= 0.7
            RETURN node.text AS text, node.pleasure AS pleasure, node.arousal AS arousal, node.retrieval_count AS retrieval_count, score
            ORDER BY score DESC LIMIT 1
            """
            params = {"text": sanitized_text[:900]}  # Truncate to avoid exceeding limits
            result = self.db.run_query(query, params)
    
            if result:
                memory = result[0]
                self.memory_cache[sanitized_text] = memory
                self.update_retrieval_stats(memory['text'])
                return memory
            else:
                logger.warning(f"[SEARCH MISS] No memory found for: {sanitized_text}")
                self.store_memory(text)  # Optionally store missing memory
                return None
    
        except Exception as e:
            logger.error(f"[SEARCH ERROR] Unable to search memory '{text}': {e}", exc_info=True)
            return None


    def store_memory(self, text: str, emotions: Optional[List[str]] = None, extra_properties: Optional[Dict] = None, pleasure: float = 0.5, arousal: float = 0.5):
        """
        Store memory in Neo4j with contextual and emotional data.
        """
        sanitized_text = self.clean_text(text.lower())
        emotions = emotions or ["neutral"]
        timestamp = datetime.now().isoformat()
    
        if not sanitized_text:
            logger.warning(f"[EMPTY QUERY] Skipping storage for empty sanitized text.")
            return
    
        try:
            query = """
            MERGE (m:Memory {text: $text})
            ON CREATE SET 
                m.created_at = $timestamp,
                m.pleasure = $pleasure,
                m.arousal = $arousal,
                m.retrieval_count = 0,
                m.emotions = $emotions
            WITH m
            UNWIND $emotions AS emotion
            MERGE (e:Emotion {name: emotion})
            MERGE (m)-[:EMOTION_OF]->(e)
            RETURN m.text AS memory_text
            """
            params = {
                "text": sanitized_text,
                "timestamp": timestamp,
                "pleasure": pleasure,
                "arousal": arousal,
                "emotions": emotions,
            }
    
            result = self.db.run_query(query, params)
            if result:
                logger.info(f"[NEW MEMORY STORED] Memory saved: {sanitized_text}")
            else:
                logger.info(f"[MEMORY EXISTS] Memory already exists in Neo4j.")
    
        except Exception as e:
            logger.error(f"[MEMORY STORAGE FAILED] Unable to store memory '{text}': {e}", exc_info=True)

    def update_retrieval_stats(self, text: str):
        """Update retrieval frequency and adjust pleasure/arousal."""
        try:
            query = """
            MATCH (m:Memory {text: $text})
            SET m.retrieval_count = COALESCE(m.retrieval_count, 0) + 1,
                m.pleasure = m.pleasure + 0.01,
                m.arousal = m.arousal - 0.01
            RETURN m.text AS updated_text, m.pleasure AS updated_pleasure,
                m.arousal AS updated_arousal, m.retrieval_count AS updated_retrieval_count
            """
            params = {"text": text}
            self.db.run_query(query, params)
            logger.info(f"[RETRIEVAL UPDATE] Attributes updated for '{text}'.")
        except Exception as e:
            logger.error(f"[ATTRIBUTE UPDATE FAILED] {e}", exc_info=True)


    def get_top_retrieved_memories(self, limit: int = 3) -> List[Dict]:
        """
        Retrieve top memories based on retrieval count.

        :param limit: The number of top memories to retrieve.
        :return: A list of memory dictionaries.
        """
        try:
            query = """
            MATCH (m:Memory)
            RETURN m.text AS text, m.retrieval_count AS retrieval_count
            ORDER BY m.retrieval_count DESC
            LIMIT $limit
            """
            params = {"limit": limit}
            result = self.db.run_query(query, params)

            logger.info(f"[TOP MEMORIES] Retrieved {len(result)} top memories.")
            return result
        except Exception as e:
            logger.error(f"[RETRIEVE TOP MEMORIES ERROR] {e}", exc_info=True)
            return []

    def cluster_related_memories(self):
        """
        Cluster memories based on similarity and themes for better organization.
    
        :return: Clustering results.
        """
        query = """
        CALL gds.beta.nodeSimilarity.stream({
            nodeProjection: 'Memory',
            relationshipProjection: 'RELATED_TO'
        })
        YIELD node1, node2, similarity
        RETURN gds.util.asNode(node1).text AS memory1, gds.util.asNode(node2).text AS memory2, similarity
        """
        try:
            result = self.db.run_query(query)
            logger.info(f"[CLUSTERING] Clustered memories: {len(result)} relationships identified.")
            return result
        except Exception as e:
            logger.error(f"[CLUSTERING ERROR] {e}")
    
    def multi_dimensional_search(self, query_text: str, emotion_filter: str = None) -> List[Dict]:
        """
        Search memories using text, theme, and optional emotion filter.
    
        :param query_text: Text to search for.
        :param emotion_filter: Filter results by emotion if specified.
        :return: List of matching memories.
        """
        try:
            sanitized_query = self.clean_text(query_text)
            query = f"""
            CALL db.index.fulltext.queryNodes('memoryIndex', '{sanitized_query}') YIELD node, score
            WHERE {f"node.emotion = '{emotion_filter}' AND " if emotion_filter else ""}score > 0.5
            RETURN node.text AS text, node.theme AS theme, node.emotion AS emotion, score
            ORDER BY score DESC
            """
            result = self.db.run_query(query)
            logger.info(f"[SEARCH] Found {len(result)} results for query: {query_text}")
            return result
        except Exception as e:
            logger.error(f"[SEARCH ERROR] {e}")
            return []