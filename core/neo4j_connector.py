# Updated Neo4j Connector
from neo4j import GraphDatabase, exceptions
import logging
import time

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

class Neo4jConnector:
    def __init__(self, uri, user, password, max_retries=3, retry_delay=3):
        self.uri = uri
        self.user = user
        self.password = password
        self.max_retries = max_retries
        self.retry_delay = retry_delay
        self.driver = self._connect_with_retry()

    def _connect_with_retry(self):
        for attempt in range(self.max_retries):
            try:
                driver = GraphDatabase.driver(self.uri, auth=(self.user, self.password))
                with driver.session() as session:
                    session.run("RETURN 1")
                logger.info("[Neo4j] Connected successfully.")
                return driver
            except exceptions.AuthError:
                logger.error("[AUTH ERROR] Invalid credentials for Neo4j.")
                raise
            except exceptions.ServiceUnavailable:
                logger.warning(f"[CONNECTION FAILED] Attempt {attempt + 1} failed.")
                time.sleep(self.retry_delay)
        raise Exception("Failed to connect after multiple attempts.")

    def run_query(self, query, parameters=None, db=None):
        try:
            with self.driver.session(database=db) if db else self.driver.session() as session:
                result = session.run(query, parameters)
                data = result.data()
                logger.info(f"[QUERY SUCCESS] {len(data)} rows returned.")
                return data
        except Exception as e:
            logger.error(f"[QUERY FAILED] {e}", exc_info=True)
            return []

    def close(self):
        self.driver.close()
        logger.info("[CONNECTION CLOSED] Neo4j driver closed.")