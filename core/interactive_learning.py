# File: /core/interactive_learning.py

class InteractiveLearning:
    def __init__(self, graph_client):
        self.graph_client = graph_client

    def identify_knowledge_gaps(self):
        query = """
        MATCH (n:Emotion)
        WHERE NOT EXISTS(n.example_context)
        RETURN n.id AS id, n.name AS name
        """
        return self.graph_client.run_query(query)

    def ask_questions(self, knowledge_gaps):
        for gap in knowledge_gaps:
            print(f"Help me understand '{gap['name']}' better!")
            example_context = input(f"Can you give me an example of {gap['name']}? ")
            self.graph_client.run_query(f"""
            MATCH (n:Emotion {{id: '{gap['id']}'}})
            SET n.example_context = '{example_context}'
            """)
