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
        wrapped_text = self.prepare_query_text(sanitized_text)

        if not wrapped_text:
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
            params = {"text": wrapped_text[:900]}  # Truncate to avoid exceeding limits
            result = self.db.run_query(query, params)

            if result:
                memory = result[0]
                self.memory_cache[sanitized_text] = memory
                self.update_retrieval_stats(memory['text'])
                return memory
            else:
                logger.warning(f"[SEARCH MISS] No memory found for: {sanitized_text}")
                # Optionally store missing memory
                self.store_memory(text)
                return None

        except Exception as e:
            logger.error(f"[SEARCH ERROR] Unable to search memory '{text}': {e}", exc_info=True)
            return None

    def store_memory(self, text: str, emotions: Optional[List[str]] = None, extra_properties: Optional[Dict] = None, pleasure: float = 0.5, arousal: float = 0.5):
        """
        Store memory in Neo4j with contextual and emotional data, handling large texts by chunking and sanitizing input.
        """
        sanitized_text = self.clean_text(text.lower())
        emotions = emotions or ["neutral"]
        timestamp = datetime.now().isoformat()

        if not sanitized_text:
            logger.warning(f"[EMPTY QUERY] Skipping storage for empty sanitized text.")
            return

        # Define chunk size for storage and truncation size for queries
        chunk_size = 900  # Maximum query length Neo4j allows with safety margin
        chunks = [sanitized_text[i:i + chunk_size] for i in range(0, len(sanitized_text), chunk_size)]

        try:
            for index, chunk in enumerate(chunks, start=1):
                logger.info(f"[CHUNK PROCESSING] Processing chunk {index}/{len(chunks)}.")

                # Escape special characters in chunk to avoid parser errors
                escaped_chunk = re.sub(r'([:+\-~<>])', r'\\\1', chunk)

                # Check for similar memories using the escaped and truncated text
                query_similarity = """
                CALL db.index.fulltext.queryNodes('memoryIndex', $text) YIELD node, score
                WHERE score >= 0.7
                RETURN node.text AS existing_text, node.pleasure AS existing_pleasure,
                    node.arousal AS existing_arousal, node.retrieval_count AS existing_retrieval_count, score
                ORDER BY score DESC LIMIT 1
                """
                params_similarity = {"text": escaped_chunk}
                result_similarity = self.db.run_query(query_similarity, params_similarity)

                if result_similarity and result_similarity[0]['score'] >= 0.7:
                    # Link chunk to similar memory
                    similar_text = result_similarity[0]['existing_text']
                    similarity_score = result_similarity[0]['score']

                    query_linking = """
                    MATCH (m1:Memory {text: $similar_text})
                    MERGE (m2:Memory {text: $new_text})
                    ON CREATE SET 
                        m2.created_at = COALESCE($timestamp, datetime()),
                        m2.pleasure = $pleasure,
                        m2.arousal = $arousal,
                        m2.retrieval_count = 0,
                        m2.emotions = $emotions,
                        m2.chunk_index = $chunk_index,
                        m2.source = $source,
                        m2.type = $type
                    MERGE (m1)-[:SIMILAR_TO {score: $similarity_score}]->(m2)
                    WITH m2
                    UNWIND $emotions AS emotion
                    MERGE (e:Emotion {name: emotion})
                    MERGE (m2)-[:EMOTION_OF]->(e)
                    RETURN m2.text AS memory_text, COUNT(m2) > 0 AS new_memory
                    """
                    params_linking = {
                        "similar_text": similar_text,
                        "new_text": chunk,
                        "timestamp": timestamp,
                        "pleasure": pleasure,
                        "arousal": arousal,
                        "emotions": emotions,
                        "similarity_score": similarity_score,
                        "chunk_index": index,
                        "source": extra_properties.get("source", "unknown"),
                        "type": extra_properties.get("type", "file_upload"),
                    }

                    result_linking = self.db.run_query(query_linking, params_linking)
                    logger.info(f"[LINKED MEMORY] Chunk {index}/{len(chunks)} linked to '{similar_text}' with similarity {similarity_score}.")
                else:
                    # Store as a new memory
                    query_store = """
                    MERGE (m:Memory {text: $text})
                    ON CREATE SET 
                        m.created_at = COALESCE($timestamp, datetime()),
                        m.pleasure = $pleasure,
                        m.arousal = $arousal,
                        m.retrieval_count = 0,
                        m.emotions = $emotions,
                        m.chunk_index = $chunk_index,
                        m.source = $source,
                        m.type = $type
                    WITH m
                    UNWIND $emotions AS emotion
                    MERGE (e:Emotion {name: emotion})
                    MERGE (m)-[:EMOTION_OF]->(e)
                    RETURN m.text AS memory_text, COUNT(m) > 0 AS new_memory
                    """
                    params_store = {
                        "text": chunk,
                        "timestamp": timestamp,
                        "pleasure": pleasure,
                        "arousal": arousal,
                        "emotions": emotions,
                        "chunk_index": index,
                        "source": extra_properties.get("source", "unknown"),
                        "type": extra_properties.get("type", "file_upload"),
                    }

                    result_store = self.db.run_query(query_store, params_store)
                    if result_store and result_store[0].get("new_memory"):
                        logger.info(f"[NEW MEMORY STORED] Chunk {index}/{len(chunks)} saved in Neo4j.")
                    else:
                        logger.info(f"[EXISTING MEMORY MATCHED] Chunk {index}/{len(chunks)} already exists in Neo4j.")

                # Update memory cache for each chunk
                self.memory_cache[chunk] = {
                    "text": chunk,
                    "emotions": emotions,
                    "pleasure": pleasure,
                    "arousal": arousal,
                    "timestamp": timestamp,
                    "chunk_index": index,
                }
                logger.info(f"[CACHE UPDATE] Chunk {index}/{len(chunks)} stored in cache.")

        except Exception as e:
            logger.error(f"[MEMORY STORAGE FAILED] Unable to store memory '{text}': {e}", exc_info=True)


    def update_retrieval_stats(self, text: str) -> Optional[Dict]:
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
            result = self.db.run_query(query, params)
            if result:
                logger.info(f"[ATTRIBUTE UPDATE] Attributes updated for '{text}': {result[0]}")
                return result[0]
            else:
                logger.warning(f"[NO MEMORY FOUND] Unable to update attributes for '{text}'.")
                return None
        except Exception as e:
            logger.error(f"[ATTRIBUTE UPDATE FAILED] Unable to update attributes for '{text}': {e}", exc_info=True)
            return None

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