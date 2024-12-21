# File: /core/feedback_loops.py

class FeedbackLoops:
    def __init__(self, graph_client):
        self.graph_client = graph_client

    def prompt_user_validation(self, node_id, name, attributes):
        print(f"Validate the attributes of '{name}': {attributes}")
        valid = input("Is this correct? (yes/no): ").lower()
        if valid == "no":
            updated_attributes = input("Enter correct attributes (key=value pairs): ")
            self.graph_client.run_query(f"""
            MATCH (n)
            WHERE n.id = '{node_id}'
            SET {", ".join([f"n.{kv.split('=')[0]} = '{kv.split('=')[1]}'" for kv in updated_attributes.split(",")])}
            """)
