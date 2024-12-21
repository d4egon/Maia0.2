from neo4j import GraphDatabase
from dotenv import load_dotenv
import os

# Load Environment Variables
load_dotenv()

# Connect to Neo4j
uri = os.getenv("NEO4J_URI")
user = os.getenv("NEO4J_USER")
password = os.getenv("NEO4J_PASSWORD")

driver = GraphDatabase.driver(uri, auth=(user, password))

def test_connection(tx):
    query = "RETURN 'Neo4j Connected' AS message"
    result = tx.run(query)
    return result.single()["message"]

try:
    with driver.session() as session:
        message = session.execute_read(test_connection)
        print(message)
except Exception as e:
    print(f"Connection Error: {e}")
finally:
    driver.close()
