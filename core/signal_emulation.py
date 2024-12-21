# /core/signal_emulation.py

class SignalPropagation:
    def __init__(self, brain_interface):
        self.brain = brain_interface

    def send_signal(self, start_node_name, max_hops=5):
        """Send a signal through the graph from the starting node."""
        with self.brain.driver.session() as session:
            result = session.run(
                """
                MATCH path = (start:Node {name: $start_node_name})-[*..$max_hops]->(end)
                RETURN path
                """,
                start_node_name=start_node_name,
                max_hops=max_hops
            )
            return [record["path"] for record in result]
