# File: /core/deduplication_engine.py

from neo4j import GraphDatabase
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import logging
from typing import List, Tuple

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DeduplicationEngine:
    def __init__(self, uri: str, user: str, password: str):
        """
        Initialize the DeduplicationEngine with Neo4j connection details.

        :param uri: Neo4j database URI
        :param user: Database username
        :param password: Database password
        """
        self.driver = GraphDatabase.driver(uri, auth=(user, password))

    def close(self):
        """
        Close the Neo4j driver connection.
        """
        if self.driver:
            self.driver.close()
            logger.info("Neo4j driver closed.")

    def find_duplicates(self, label: str = "Emotion") -> List[Tuple[str, str, str]]:
        """
        Find potential duplicate nodes based on label.

        :param label: The node label to check for duplicates.
        :return: List of tuples containing id, name, and description of nodes.
        """
        query = f"""
        MATCH (e:{label})
        RETURN e.id AS id, e.name AS name, e.description AS description
        """
        try:
            with self.driver.session() as session:
                result = session.run(query)
                nodes = [(record["id"], record["name"], record["description"]) for record in result]
                logger.info(f"Found {len(nodes)} nodes for deduplication with label {label}.")
                return nodes
        except Exception as e:
            logger.error(f"Error finding duplicates: {e}")
            raise

    def merge_duplicates(self, duplicates: List[List[str]]):
        """
        Merge duplicate nodes into one.

        :param duplicates: List of lists where each inner list contains IDs of nodes to be merged.
        """
        try:
            with self.driver.session() as session:
                for duplicate_group in duplicates:
                    if len(duplicate_group) < 2:  # Skip if there's only one node
                        continue
                    base_node = duplicate_group[0]
                    for duplicate in duplicate_group[1:]:
                        merge_query = f"""
                        MATCH (n1), (n2)
                        WHERE n1.id = '{base_node}' AND n2.id = '{duplicate}'
                        WITH n1, n2
                        CALL apoc.refactor.mergeNodes([n1, n2]) YIELD node
                        RETURN node
                        """
                        session.run(merge_query)
                        logger.info(f"Merged node {duplicate} into {base_node}")
        except Exception as e:
            logger.error(f"Error merging duplicates: {e}")
            raise

    def deduplicate(self, label: str = "Emotion"):
        """
        Perform deduplication by finding and merging nodes based on description similarity.

        :param label: The label of nodes to deduplicate.
        """
        try:
            nodes = self.find_duplicates(label)
            descriptions = [desc for _, _, desc in nodes if desc]  # Filter out nodes without descriptions
            if not descriptions:
                logger.info("No descriptions found for deduplication.")
                return

            vectorizer = TfidfVectorizer().fit_transform(descriptions)
            similarity_matrix = cosine_similarity(vectorizer)
            duplicates = []
            for idx, row in enumerate(similarity_matrix):
                similar_nodes = [nodes[i][0] for i in range(len(row)) if row[i] > 0.85 and i != idx]
                if similar_nodes:
                    duplicates.append([nodes[idx][0]] + similar_nodes)

            logger.info(f"Identified {len(duplicates)} groups of duplicates to merge.")
            self.merge_duplicates(duplicates)
        except Exception as e:
            logger.error(f"Error during deduplication process: {e}")
            raise

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()