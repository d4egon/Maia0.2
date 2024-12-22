# Filename: /core/context_search.py

import logging
from sentence_transformers import SentenceTransformer, util
from typing import List, Dict, Optional

# Initialize logging
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class SentenceParser:
    def __init__(self):
        """
        Initialize SentenceParser with a sentence transformer model for embeddings.
        """
        self.embedding_model = SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')

    def parse_and_search(self, input_text: str, memory_engine) -> Dict:
        """
        Parse input text to find the best matching memory using embeddings.

        :param input_text: The text to search for.
        :param memory_engine: An object with a `search_memory` method to fetch memories.
        :return: Dictionary with the best match or a message if no match found.
        """
        try:
            input_embedding = self.embedding_model.encode(input_text.lower(), convert_to_tensor=True)
            memories = memory_engine.search_memory(input_text)

            if not memories:
                logger.info(f"[MEMORY SEARCH] No memories found for '{input_text}'")
                return {"result": "No matching memory found."}

            best_match = max(memories, key=lambda m: util.cos_sim(input_embedding, self.embedding_model.encode(m["text"].lower())), default=None)
            return best_match if best_match else {"result": "No matching memory found."}
        except Exception as e:
            logger.error(f"[PARSE & SEARCH FAILED] {e}", exc_info=True)
            return {"result": "Error in processing search."}

class ContextSearchEngine:
    def __init__(self, neo4j_connector):
        """
        Initialize ContextSearchEngine with Neo4j connector and sentence embedding model.

        :param neo4j_connector: An instance of Neo4jConnector for database operations.
        """
        self.db = neo4j_connector
        self.embedding_model = SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')

    def search_related_contexts(self, text: str, similarity_threshold: float = 0.7) -> List[Dict]:
        """
        Search for related contexts in the database based on semantic similarity.

        :param text: Text to find related contexts for.
        :param similarity_threshold: Minimum cosine similarity score to consider a match.
        :return: List of dictionaries with related memories and their similarity scores.
        """
        try:
            # First, get potentially related contexts via full-text search
            query = """
            CALL db.index.fulltext.queryNodes('memoryIndex', $text)
            YIELD node, score
            RETURN node.text AS Memory, node.weight AS Weight, score
            ORDER BY score DESC LIMIT 20
            """
            results = self.db.run_query(query, {"text": text.lower()})

            if not results:
                logger.info(f"[CONTEXT SEARCH] No memories found for '{text}'")
                return []

            input_embedding = self.embedding_model.encode(text.lower(), convert_to_tensor=True)
            filtered_results = []
            for record in results:
                memory_text = record["Memory"]
                memory_embedding = self.embedding_model.encode(memory_text.lower(), convert_to_tensor=True)
                similarity_score = util.cos_sim(input_embedding, memory_embedding).item()

                if similarity_score >= similarity_threshold:
                    filtered_results.append({
                        "memory": memory_text,
                        "weight": record["Weight"],
                        "similarity": round(similarity_score, 2)
                    })

            logger.info(f"[CONTEXT SEARCH] Found {len(filtered_results)} relevant contexts.")
            return filtered_results
        except Exception as e:
            logger.error(f"[SEARCH FAILED] {e}", exc_info=True)
            return []

    def create_dynamic_links(self, source_text: str, related_memories: List[Dict], link_type: str = "RELATED_TO"):
        """
        Create dynamic relationships in the graph database based on contextual matching.

        :param source_text: The source memory text.
        :param related_memories: List of dictionaries containing related memory texts.
        :param link_type: Type of relationship to create.
        """
        try:
            for memory in related_memories:
                query = f"""
                MATCH (s:Memory {{text: $source_text}})
                MERGE (r:Memory {{text: $related_text}})
                MERGE (s)-[:{link_type}]->(r)
                """
                self.db.run_query(query, {
                    "source_text": source_text.lower(),
                    "related_text": memory["memory"].lower()
                })
                logger.info(f"[LINK CREATED] '{source_text}' ↔ '{memory['memory']}'")
        except Exception as e:
            logger.error(f"[LINK CREATION FAILED] {e}", exc_info=True)