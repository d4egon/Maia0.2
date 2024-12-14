# Filename: tests/test_memory_engine.py

import sys, os, unittest
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from core.memory_engine import MemoryEngine
from core.neo4j_connector import Neo4jConnector
from config.settings import CONFIG

class TestMemoryEngine(unittest.TestCase):
    def setUp(self):
        self.neo4j = Neo4jConnector(CONFIG["NEO4J_URI"], CONFIG["NEO4J_USER"], CONFIG["NEO4J_PASS"])
        self.memory_engine = MemoryEngine(self.neo4j)

    def test_store_memory(self):
        self.memory_engine.store_memory("test memory", "neutral")
        result = self.memory_engine.search_memory("test memory")
        self.assertIsNotNone(result)

if __name__ == "__main__":
    unittest.main()