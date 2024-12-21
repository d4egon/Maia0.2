# File: /core/deduplication_engine.py

from neo4j import GraphDatabase
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

class DeduplicationEngine:
    def __init__(self, uri, user, password):
        self.driver = GraphDatabase.driver(uri, auth=(user, password))
    
    def close(self):
        self.driver.close()

    def find_duplicates(self, label="Emotion"):
        query = f"""
        MATCH (e:{label})
        RETURN e.name AS name, e.id AS id, e.description AS description
        """
        with self.driver.session() as session:
            result = session.run(query)
            return [(record["id"], record["name"], record["description"]) for record in result]

    def merge_duplicates(self, duplicates):
        with self.driver.session() as session:
            for duplicate_group in duplicates:
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

    def deduplicate(self, label="Emotion"):
        nodes = self.find_duplicates(label)
        descriptions = [desc for _, _, desc in nodes if desc]
        vectorizer = TfidfVectorizer().fit_transform(descriptions)
        similarity_matrix = cosine_similarity(vectorizer)
        duplicates = []
        for idx, row in enumerate(similarity_matrix):
            similar_nodes = [nodes[i][0] for i in range(len(row)) if row[i] > 0.85 and i != idx]
            if similar_nodes:
                duplicates.append([nodes[idx][0]] + similar_nodes)
        self.merge_duplicates(duplicates)
