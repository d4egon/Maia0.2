# File: /core/attribute_enrichment.py

import requests

class AttributeEnrichment:
    def __init__(self, graph_client):
        self.graph_client = graph_client

    def get_missing_attributes(self, label="Emotion"):
        query = f"""
        MATCH (e:{label})
        WHERE NOT EXISTS(e.intensity) OR NOT EXISTS(e.category)
        RETURN e.id AS id, e.name AS name
        """
        return self.graph_client.run_query(query)

    def enrich_attributes(self, node_id, attributes):
        update_query = f"""
        MATCH (e)
        WHERE e.id = '{node_id}'
        SET {", ".join([f"e.{key} = '{value}'" for key, value in attributes.items()])}
        RETURN e
        """
        self.graph_client.run_query(update_query)

    def interactive_enrichment(self, missing_nodes):
        for node in missing_nodes:
            print(f"Node {node['name']} is missing attributes.")
            intensity = input("Enter intensity (low, medium, high): ")
            category = input("Enter category (e.g., positive, negative): ")
            self.enrich_attributes(node['id'], {"intensity": intensity, "category": category})

    def auto_enrichment(self, node_id, name):
        response = requests.get(f"https://emotion-api.example.com/lookup?name={name}")
        if response.status_code == 200:
            data = response.json()
            self.enrich_attributes(node_id, data)
