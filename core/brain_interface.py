# File: /core/brain_interface.py

from neo4j import GraphDatabase, Driver
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class BrainInterface:
    def __init__(self, uri, user, password):
        """
        Initialize the BrainInterface with Neo4j database connection details.

        :param uri: The URI of the Neo4j database.
        :param user: Username for database authentication.
        :param password: Password for database authentication.
        """
        self.driver: Driver = GraphDatabase.driver(uri, auth=(user, password))

    def close(self):
        """Close the Neo4j driver connection."""
        if self.driver:
            self.driver.close()

    def create_node(self, node_type, name, additional_properties=None):
        """
        Create or merge a node in the database.

        :param node_type: The type of the node (label).
        :param name: The name of the node.
        :param additional_properties: Additional properties for the node.
        :return: The created or merged node.
        :raises Exception: If there's an error during node creation.
        """
        additional_properties = additional_properties or {}
        with self.driver.session() as session:
            try:
                result = session.run(
                    """
                    MERGE (n:`{node_type}` {{name: $name}})
                    SET n += $additional_properties
                    RETURN n
                    """.format(node_type=node_type),
                    name=name,
                    additional_properties=additional_properties
                )
                node = result.single()
                if node:
                    logger.info(f"Node created or merged: {node['n']}")
                    return node['n']
                else:
                    logger.warning("No node was returned from the query.")
                    return None
            except Exception as e:
                logger.error(f"Error creating node: {e}")
                raise

    def create_relationship(self, source_name, target_name, relationship_type, properties=None):
        """
        Create or merge a relationship between two nodes.

        :param source_name: Name of the source node.
        :param target_name: Name of the target node.
        :param relationship_type: Type of the relationship.
        :param properties: Additional properties for the relationship.
        :return: The result of the relationship creation query.
        :raises Exception: If there's an error during relationship creation.
        """
        properties = properties or {}
        with self.driver.session() as session:
            try:
                result = session.run(
                    """
                    MATCH (source:Node {name: $source_name}), (target:Node {name: $target_name})
                    MERGE (source)-[r:`{relationship_type}`]->(target)
                    SET r += $properties
                    RETURN source, r, target
                    """.format(relationship_type=relationship_type),
                    source_name=source_name,
                    target_name=target_name,
                    properties=properties
                )
                record = result.single()
                if record:
                    logger.info(f"Relationship created or merged: {record['r']}")
                    return record
                else:
                    logger.warning("No relationship was returned from the query.")
                    return None
            except Exception as e:
                logger.error(f"Error creating relationship: {e}")
                raise

    def get_connections(self, node_name):
        """
        Retrieve all relationships for a specific node.

        :param node_name: The name of the node to query connections for.
        :return: List of tuples with relationship types and connected node names.
        :raises Exception: If there's an error querying connections.
        """
        with self.driver.session() as session:
            try:
                result = session.run(
                    """
                    MATCH (n:Node {name: $node_name})-[r]->(m)
                    RETURN type(r) AS rel_type, m.name AS connected_node
                    """,
                    node_name=node_name
                )
                connections = [(record["rel_type"], record["connected_node"]) for record in result]
                logger.info(f"Retrieved connections for node: {node_name}")
                return connections
            except Exception as e:
                logger.error(f"Error retrieving connections: {e}")
                raise

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()