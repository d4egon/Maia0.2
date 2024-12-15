# Filename: /core/neo4j_connector.py

from neo4j import GraphDatabase, TransactionError
import logging

# Initialize logging
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

class Neo4jConnector:
    def __init__(self, uri, user, password):
        """
        Initialize the Neo4j driver.
        """
        self.driver = GraphDatabase.driver(uri, auth=(user, password))
        logger.info("[INIT] Connected to Neo4j successfully.")

    def run_query(self, query, parameters=None, db=None):
        """
        Execute a query with optional parameters and return data.
        """
        try:
            with self.driver.session(database=db) if db else self.driver.session() as session:
                result = session.run(query, parameters)
                data = result.data()
                logger.debug(f"[QUERY SUCCESS] {query} | Data: {data}")
                return data
        except TransactionError as e:
            logger.error(f"[QUERY FAILED] {e}", exc_info=True)
            return []

    def run_transaction(self, query_function, parameters=None):
        """
        Execute a transaction safely using a callback function.
        """
        try:
            with self.driver.session() as session:
                result = session.write_transaction(query_function, parameters)
                logger.info(f"[TRANSACTION SUCCESS] {result}")
                return result
        except Exception as e:
            logger.error(f"[TRANSACTION FAILED] {e}", exc_info=True)
            return None

    def create_trigger(self, trigger_name, trigger_query):
        """
        Create a Neo4j trigger using APOC.
        """
        query = f"""
        CALL apoc.trigger.add(
            '{trigger_name}',
            '{trigger_query}',
            {{phase: 'after'}}
        )
        """
        self.run_query(query)
        logger.info(f"[TRIGGER CREATED] {trigger_name}")

    def delete_trigger(self, trigger_name):
        """
        Delete a Neo4j trigger by name.
        """
        query = f"CALL apoc.trigger.remove('{trigger_name}')"
        self.run_query(query)
        logger.info(f"[TRIGGER DELETED] {trigger_name}")

    def list_triggers(self):
        """
        List all active Neo4j triggers.
        """
        query = "CALL apoc.trigger.list()"
        triggers = self.run_query(query)
        logger.info(f"[TRIGGER LIST] Found {len(triggers)} triggers.")
        return triggers

    def close(self):
        """
        Close the Neo4j driver connection gracefully.
        """
        self.driver.close()
        logger.info("[CONNECTION CLOSED] Neo4j driver connection closed.")
