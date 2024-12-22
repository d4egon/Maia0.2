# File: /core/signal_emulation.py

from neo4j import GraphDatabase

class SignalPropagation:
    def __init__(self, brain_interface):
        """
        Initialize SignalPropagation with a brain interface.

        :param brain_interface: An object with a Neo4j driver for database operations.
        """
        self.brain = brain_interface

    def send_signal(self, start_node_name, max_hops=5, node_label="Node"):
        """
        Send a signal through the graph from the starting node.

        :param start_node_name: Name of the starting node.
        :param max_hops: Maximum number of hops the signal can travel (default 5).
        :param node_label: Label of nodes to consider in the path (default "Node").
        :return: List of paths representing the signal propagation.
        :raises ValueError: If max_hops is not positive.
        :raises Neo4jError: If there's an issue with the database operation.
        """
        if max_hops <= 0:
            raise ValueError("max_hops must be a positive integer")

        with self.brain.driver.session() as session:
            try:
                # Use parameterized queries to prevent injection vulnerabilities
                result = session.run(
                    """
                    MATCH path = (:`{node_label}` {{name: $start_node_name}})-[*..$max_hops]->(end)
                    RETURN path
                    """.format(node_label=node_label),
                    start_node_name=start_node_name,
                    max_hops=max_hops
                )
                # Convert paths to strings for easier handling or serialization if needed
                paths = [str(record["path"]) for record in result]
                return paths
            except GraphDatabase.DatabaseError as e:
                # Log the error for debugging
                print(f"Database error occurred: {e}")
                raise
            except Exception as e:
                # Log unexpected errors
                print(f"An unexpected error occurred: {e}")
                raise

    def get_signal_strength(self, path):
        """
        Calculate signal strength based on path length. 
        This is a simple placeholder and can be enhanced for more realistic signal degradation.

        :param path: A string representation of the path.
        :return: A float representing signal strength (0.0 to 1.0).
        """
        # Here, we assume strength decreases linearly with path length
        path_length = len(path.split('-')) - 1  # Count relationships, not nodes
        return max(0.0, 1.0 - (path_length / 10.0))  # Arbitrary strength calculation