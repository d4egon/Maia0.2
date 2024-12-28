# File: /core/semantic_builder.py

import torch
from transformers import pipeline
from sklearn.metrics.pairwise import cosine_similarity
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SemanticBuilder:
    def __init__(self, graph_client, similarity_threshold=0.8):
        self.graph_client = graph_client
        self.similarity_model = pipeline("text-similarity", model="all-MiniLM-L6-v2")
        self.similarity_threshold = similarity_threshold

    def compute_similarities(self, embeddings):
        """
        Compute cosine similarity between all pairs of embeddings.

        :param embeddings: List of embedding vectors
        :return: Similarity matrix
        """
        embeddings_tensor = torch.tensor(embeddings)
        return cosine_similarity(embeddings_tensor)

    def build_relationships(self, label="Emotion", relationship_type="SIMILAR_TO"):
        """
        Build relationships in the graph based on similarity of node descriptions.

        :param label: The label of nodes to analyze
        :param relationship_type: Type of relationship to create based on similarity
        """
        query = f"""
        MATCH (e:{label})
        RETURN e.id AS id, e.name AS name, e.description AS description
        """
        try:
            nodes = self.graph_client.run_query(query)
            descriptions = [node["description"] for node in nodes if node["description"]]
            
            if not descriptions:
                logger.warning(f"No descriptions found for label: {label}")
                return

            embeddings = self.similarity_model(descriptions)
            similarities = self.compute_similarities(embeddings)

            batch_size = 1000
            for i in range(0, len(similarities), batch_size):
                for j in range(i + 1, min(i + batch_size, len(similarities))):
                    if similarities[i][j] > self.similarity_threshold:
                        self.create_relationship(nodes[i]['id'], nodes[j]['id'], relationship_type)

        except Exception as e:
            logger.error(f"Error building relationships: {e}")

    def create_relationship(self, id1, id2, relationship_type):
        """
        Create a relationship between two nodes in the graph.

        :param id1: ID of the first node
        :param id2: ID of the second node
        :param relationship_type: Type of relationship to establish
        """
        query = f"""
        MATCH (n1), (n2)
        WHERE n1.id = '{id1}' AND n2.id = '{id2}'
        MERGE (n1)-[:{relationship_type}]->(n2)
        """
        try:
            self.graph_client.run_query(query)
            logger.info(f"Relationship {relationship_type} created between {id1} and {id2}")
        except Exception as e:
            logger.error(f"Failed to create relationship between {id1} and {id2}: {e}")

    def detect_narrative_shifts(self):
        """
        Detect shifts in narrative themes in the graph.
    
        :return: List of detected shifts.
        """
        query = """
        MATCH (m:Memory)
        RETURN m.text AS text, m.theme AS theme, m.timestamp AS timestamp
        ORDER BY m.timestamp
        """
        try:
            nodes = self.graph_client.run_query(query)
            shifts = []
            for i in range(1, len(nodes)):
                if nodes[i]["theme"] != nodes[i - 1]["theme"]:
                    shifts.append(f"Shift from {nodes[i - 1]['theme']} to {nodes[i]['theme']} at {nodes[i]['timestamp']}.")
            logger.info(f"[NARRATIVE SHIFTS] Detected {len(shifts)} shifts.")
            return shifts
        except Exception as e:
            logger.error(f"[SHIFT DETECTION ERROR] {e}")
            return []


# Usage example:
# sb = SemanticBuilder(graph_client)
# sb.build_relationships(label="Emotion", relationship_type="SIMILAR_TO")