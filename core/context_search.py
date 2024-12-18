# Filename: /core/context_search.py

import logging
from sentence_transformers import SentenceTransformer, util

# Initialize logging
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

class SentenceParser:
    def __init__(self):
        self.embedding_model = SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')

    def parse_and_search(self, input_text, memory_engine):
        embedding = self.embedding_model.encode(input_text.lower(), convert_to_tensor=True)
        memories = memory_engine.search_memory(input_text)

        # Use embedding similarity to improve search
        best_match = max(memories, key=lambda m: util.cos_sim(embedding, self.embedding_model.encode(m["text"].lower())), default=None)
        return best_match if best_match else "No matching memory found."

class ContextSearchEngine:
    def __init__(self, neo4j_connector):
        self.db = neo4j_connector
        # Load pre-trained sentence-transformer model
        self.embedding_model = SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')

    def search_related_contexts(self, text, similarity_threshold=0.7):
        """
        Find related contexts in the database using deep learning sentence embeddings.
        """
        try:
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

            # Embed the input text
            input_embedding = self.embedding_model.encode(text.lower(), convert_to_tensor=True)

            # Calculate semantic similarity
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

    def find_contextual_links(self, memory_text, link_type="RELATED_TO"):
        """
        Find directly linked memories from the graph database.
        """
        try:
            query = f"""
            MATCH (m:Memory {{text: $memory_text}})-[:{link_type}]-(related:Memory)
            RETURN related.text AS Memory, related.weight AS Weight
            ORDER BY related.weight DESC LIMIT 10
            """
            results = self.db.run_query(query, {"memory_text": memory_text.lower()})
            logger.info(f"[LINK SEARCH] Found {len(results)} linked memories.")
            return results
        except Exception as e:
            logger.error(f"[LINK SEARCH FAILED] {e}", exc_info=True)
            return []

    def create_dynamic_links(self, source_text, related_memories, link_type="RELATED_TO"):
        """
        Automatically create dynamic relationships in the graph database
        based on contextual matching using deep learning.
        """
        try:
            for memory in related_memories:
                query = f"""
                MATCH (s:Memory {{text: $source_text}})
                MATCH (r:Memory {{text: $related_text}})
                MERGE (s)-[:{link_type}]->(r)
                """
                self.db.run_query(query, {
                    "source_text": source_text.lower(),
                    "related_text": memory["memory"].lower()
                })
                logger.info(f"[LINK CREATED] '{source_text}' ↔ '{memory['memory']}'")

        except Exception as e:
            logger.error(f"[LINK CREATION FAILED] {e}", exc_info=True)