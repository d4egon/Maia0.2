# Filename: core/context_search.py

class ContextSearchEngine:
    def __init__(self, neo4j_connector):
        self.db = neo4j_connector

    def search_related_contexts(self, text):
        """
        Finds related contexts in the database using semantic similarity.
        """
        query = """
        CALL db.index.fulltext.queryNodes('memoryIndex', $text)
        YIELD node, score
        RETURN node.text AS Memory, node.weight AS Weight, score
        ORDER BY score DESC LIMIT 5
        """
        result = self.db.run_query(query, {"text": text.lower()})
        return [{"memory": record["Memory"], "weight": record["Weight"], "score": record["score"]} for record in result]

    def find_contextual_links(self, memory_text):
        """
        Finds linked memories from the graph database.
        """
        query = """
        MATCH (m:Memory {text: $memory_text})-[:RELATED_TO]-(related:Memory)
        RETURN related.text AS Memory, related.weight AS Weight
        ORDER BY related.weight DESC LIMIT 5
        """
        result = self.db.run_query(query, {"memory_text": memory_text.lower()})
        return [{"memory": record["Memory"], "weight": record["Weight"]} for record in result]