# /core/brain_interface.py

from neo4j import GraphDatabase

class BrainInterface:
    def __init__(self, uri, user, password):
        self.driver = GraphDatabase.driver(uri, auth=(user, password))

    def close(self):
        self.driver.close()

    def create_node(self, node_type, name, additional_properties=None):
        """Create a node in the database."""
        with self.driver.session() as session:
            result = session.run(
                """
                MERGE (n:Node {type: $node_type, name: $name})
                SET n += $additional_properties
                RETURN n
                """,
                node_type=node_type,
                name=name,
                additional_properties=additional_properties or {}
            )
            return result.single()[0]

    def create_relationship(self, source_name, target_name, relationship_type, properties=None):
        """Create a relationship between two nodes."""
        with self.driver.session() as session:
            result = session.run(
                """
                MATCH (source:Node {name: $source_name}), (target:Node {name: $target_name})
                MERGE (source)-[r:%s]->(target)
                SET r += $properties
                RETURN source, r, target
                """ % relationship_type,
                source_name=source_name,
                target_name=target_name,
                properties=properties or {}
            )
            return result.single()

    def get_connections(self, node_name):
        """Get all relationships for a specific node."""
        with self.driver.session() as session:
            result = session.run(
                """
                MATCH (n:Node {name: $node_name})-[r]->(m)
                RETURN r, m
                """,
                node_name=node_name
            )
            return [(record["r"].type, record["m"]["name"]) for record in result]

