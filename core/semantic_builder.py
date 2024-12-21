# File: /core/semantic_builder.py

from transformers import pipeline

class SemanticBuilder:
    def __init__(self, graph_client):
        self.graph_client = graph_client
        self.similarity_model = pipeline("text-similarity", model="all-MiniLM-L6-v2")

    def build_relationships(self, label="Emotion"):
        query = f"""
        MATCH (e:{label})
        RETURN e.id AS id, e.name AS name, e.description AS description
        """
        nodes = self.graph_client.run_query(query)
        descriptions = [node["description"] for node in nodes if node["description"]]
        embeddings = self.similarity_model([desc for desc in descriptions])
        for i, embedding1 in enumerate(embeddings):
            for j, embedding2 in enumerate(embeddings):
                if i < j and self.similarity_model(embedding1, embedding2)["similarity"] > 0.8:
                    self.graph_client.run_query(f"""
                    MATCH (n1), (n2)
                    WHERE n1.id = '{nodes[i]['id']}' AND n2.id = '{nodes[j]['id']}'
                    MERGE (n1)-[:SIMILAR_TO]->(n2)
                    """)
