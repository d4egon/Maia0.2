import logging
from datetime import datetime
from core.neo4j_connector import Neo4jConnector
import emoji
import re
from typing import Dict, List, Any, Optional
import numpy as np

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
            self.db.run_query(
                "CREATE CONSTRAINT IF NOT EXISTS FOR (t:Theme) REQUIRE t.name IS UNIQUE"
            )
            logger.info("[INDEX SETUP] Full-text index 'memoryIndex' and constraints on Emotion.name and Theme.name created or already exist.")
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
            RETURN node.text AS text, node.pleasure AS pleasure, node.arousal AS arousal, node.retrieval_count AS retrieval_count, score,
                   node.emotions AS emotions, node.theme AS theme
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
        theme = extra_properties.get("theme", "general") if extra_properties else "general"
    
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
                m.emotions = $emotions,
                m.theme = $theme
            WITH m
            UNWIND $emotions AS emotion
            MERGE (e:Emotion {name: emotion})
            MERGE (m)-[:EMOTION_OF]->(e)
            MERGE (t:Theme {name: $theme})
            MERGE (m)-[:THEME_OF]->(t)
            RETURN m.text AS memory_text
            """
            params = {
                "text": sanitized_text,
                "timestamp": timestamp,
                "pleasure": pleasure,
                "arousal": arousal,
                "emotions": emotions,
                "theme": theme,
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
                m.pleasure = CASE WHEN m.pleasure + 0.01 < 1 THEN m.pleasure + 0.01 ELSE 1 END,
                m.arousal = CASE WHEN m.arousal - 0.01 > 0 THEN m.arousal - 0.01 ELSE 0 END
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
            RETURN m.text AS text, m.retrieval_count AS retrieval_count, m.pleasure AS pleasure, m.arousal AS arousal,
                   m.emotions AS emotions, m.theme AS theme
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
        CALL apoc.nodes.similarity(['Memory'], {
            compareWith: ['text', 'theme'],
            write: true,
            similarityCutoff: 0.5,
            relationshipType: 'SIMILAR_TO'
        })
        YIELD item1, item2, similarity
        RETURN item1.text AS memory1, item2.text AS memory2, similarity
        """
        try:
            result = self.db.run_query(query)
            logger.info(f"[CLUSTERING] Clustered memories: {len(result)} relationships identified.")
            return result
        except Exception as e:
            logger.error(f"[CLUSTERING ERROR] {e}")

    def multi_dimensional_search(self, query_text: str, emotion_filter: str = None, theme_filter: str = None) -> List[Dict]:
        """
        Search memories using text, theme, and optional emotion or theme filter.
    
        :param query_text: Text to search for.
        :param emotion_filter: Filter results by emotion if specified.
        :param theme_filter: Filter results by theme if specified.
        :return: List of matching memories.
        """
        try:
            sanitized_query = self.clean_text(query_text)
            conditions = []
            if emotion_filter:
                conditions.append(f"ANY (e IN m.emotions WHERE e = '{emotion_filter}')")
            if theme_filter:
                conditions.append(f"m.theme = '{theme_filter}'")
            where_clause = " AND ".join(conditions) if conditions else "TRUE"

            query = f"""
            CALL db.index.fulltext.queryNodes('memoryIndex', '{sanitized_query}') YIELD node AS m, score
            WHERE score > 0.5 AND {where_clause}
            RETURN m.text AS text, m.theme AS theme, m.emotions AS emotions, m.pleasure AS pleasure, m.arousal AS arousal, score
            ORDER BY score DESC
            """
            result = self.db.run_query(query)
            logger.info(f"[SEARCH] Found {len(result)} results for query: {query_text}")
            return result
        except Exception as e:
            logger.error(f"[SEARCH ERROR] {e}")
            return []

    def apply_memory_decay(self):
        """
        Apply decay to memory retrieval counts and emotional intensity over time.
        """
        try:
            query = """
            MATCH (m:Memory)
            WITH m, datetime() - datetime({ epochMillis: apoc.date.parse(m.created_at, 'ms', 'iso')}) AS time_diff
            SET m.retrieval_count = round(m.retrieval_count * exp(-$decay_factor * (duration.inSeconds(time_diff).seconds / (24 * 60 * 60)))),
                m.pleasure = CASE WHEN m.pleasure - ($decay_factor / 2) > 0 THEN m.pleasure - ($decay_factor / 2) ELSE 0 END,
                m.arousal = CASE WHEN m.arousal - ($decay_factor / 2) > 0 THEN m.arousal - ($decay_factor / 2) ELSE 0 END
            """
            self.db.run_query(query, {"decay_factor": self.DECAY_FACTOR})
            logger.info(f"[MEMORY DECAY] Applied decay to memories")
        except Exception as e:
            logger.error(f"[MEMORY DECAY ERROR] {e}", exc_info=True)

    def retrieve_memories_by_theme(self, theme: str, limit: int = 10) -> List[Dict]:
        """
        Retrieve memories associated with a specific theme.

        :param theme: The theme to search for.
        :param limit: Maximum number of memories to return.
        :return: List of memory dictionaries.
        """
        try:
            query = """
            MATCH (m:Memory)-[:THEME_OF]->(t:Theme {name: $theme})
            RETURN m.text AS text, m.pleasure AS pleasure, m.arousal AS arousal, m.retrieval_count AS retrieval_count, m.emotions AS emotions
            ORDER BY m.retrieval_count DESC
            LIMIT $limit
            """
            result = self.db.run_query(query, {"theme": theme, "limit": limit})
            logger.info(f"[THEME RETRIEVAL] Retrieved {len(result)} memories for theme: {theme}")
            return result
        except Exception as e:
            logger.error(f"[THEME RETRIEVAL ERROR] {e}", exc_info=True)
            return []

    def update_memory(self, memory_text: str, field: str, value: Any):
        """
        Update a specific field of a memory.

        :param memory_text: The text of the memory to update.
                :param field: The field to update.
        :param value: The new value for the field.
        """
        try:
            query = f"""
            MATCH (m:Memory {{text: $memory_text}})
            SET m.{field} = $value
            """
            self.db.run_query(query, {"memory_text": memory_text, "value": value})
            logger.info(f"[MEMORY UPDATE] Updated field '{field}' with value '{value}' for memory: {memory_text}")
        except Exception as e:
            logger.error(f"[MEMORY UPDATE ERROR] {e}", exc_info=True)

    def link_memories(self, memory_text1: str, memory_text2: str):
        """
        Link two memories with a relationship to indicate similarity or connection.

        :param memory_text1: Text of the first memory.
        :param memory_text2: Text of the second memory.
        """
        try:
            query = """
            MATCH (m1:Memory {text: $text1}), (m2:Memory {text: $text2})
            MERGE (m1)-[:RELATED_TO]->(m2)
            """
            self.db.run_query(query, {"text1": memory_text1, "text2": memory_text2})
            logger.info(f"[MEMORY LINKING] Linked memories: '{memory_text1}' with '{memory_text2}'")
        except Exception as e:
            logger.error(f"[MEMORY LINKING ERROR] {e}", exc_info=True)

    def generate_memory_summary(self, memory_text: str) -> str:
        """
        Generate a summary or key points of a memory.

        :param memory_text: The text of the memory to summarize.
        :return: A summary of the memory.
        """
        try:
            # Placeholder for actual summarization logic; here we simulate with a simple truncation
            summary = memory_text[:50] + "..." if len(memory_text) > 50 else memory_text
            logger.info(f"[MEMORY SUMMARY] Generated summary for '{memory_text}': {summary}")
            return summary
        except Exception as e:
            logger.error(f"[SUMMARY ERROR] {e}", exc_info=True)
            return "Error generating summary."

    def retrieve_memory_for_reflection(self) -> Optional[Dict]:
        """
        Retrieve a memory for reflection based on criteria like emotional intensity or retrieval frequency.

        :return: A memory dictionary or None if no suitable memory is found.
        """
        try:
            query = """
            MATCH (m:Memory)
            WHERE m.pleasure > 0.6 OR m.arousal > 0.6 OR m.retrieval_count > 5
            RETURN m.text AS text, m.pleasure AS pleasure, m.arousal AS arousal, 
                   m.retrieval_count AS retrieval_count, m.emotions AS emotions, m.theme AS theme
            ORDER BY rand() LIMIT 1
            """
            result = self.db.run_query(query)
            if result:
                logger.info(f"[REFLECTION] Selected memory for reflection: {result[0]['text']}")
                return result[0]
            else:
                logger.warning("[REFLECTION] No suitable memory found for reflection.")
                return None
        except Exception as e:
            logger.error(f"[REFLECTION ERROR] {e}", exc_info=True)
            return None