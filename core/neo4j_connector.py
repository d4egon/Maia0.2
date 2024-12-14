# Filename: core/neo4j_connector.py

from neo4j import GraphDatabase

class Neo4jConnector:
    def __init__(self, uri, user, password):
        self.driver = GraphDatabase.driver(uri, auth=(user, password))

    def query(self, query, parameters=None):
        """
        Runs a query using Neo4j's driver and returns the data.
        """
        with self.driver.session() as session:
            return session.run(query, parameters).data()

    # Compatibility fix for run_query() usage in memory_engine.py
    def run_query(self, query, parameters=None):
        return self.query(query, parameters)

    def close(self):
        """
        Close the Neo4j driver connection.
        """
        self.driver.close()