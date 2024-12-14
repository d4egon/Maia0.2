# neo4j_connection.py - Establish Database Connection
from neo4j import GraphDatabase

class Neo4jConnection:
    def __init__(self, uri, user, password):
        self._driver = None
        try:
            self._driver = GraphDatabase.driver(uri, auth=(user, password))
            self._driver.verify_connectivity()
            print("Connected to Neo4j!")
        except Exception as e:
            print(f"Failed to create the driver: {e}")

    def close(self):
        if self._driver:
            self._driver.close()

    def query(self, query, parameters=None, db=None):
        assert self._driver is not None, "Driver not initialized!"
        session = None
        response = None
        try:
            session = self._driver.session(database=db) if db else self._driver.session()
            response = list(session.run(query, parameters))
        except Exception as e:
            print(f"Query failed: {e}")
        finally:
            if session:
                session.close()
        return response

# Example usage:
if __name__ == "__main__":
    conn = Neo4jConnection(
        uri="neo4j+s://46dc0ffd.databases.neo4j.io:7687",
        user="neo4j",
        password="4KjyYMe6ovQnU9QaRDnwP1q85Ok_rtB9l5p2yiWLgh8"
    )
    # Test query
    result = conn.query("RETURN 'Connection Successful!' AS message")
    for record in result:
        print(record["message"])
    conn.close()