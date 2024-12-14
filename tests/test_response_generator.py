# Filename: tests/test_response_generator.py

import sys, os, unittest
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from NLP.response_generator import ResponseGenerator
from core.neo4j_connector import Neo4jConnector
from core.memory_engine import MemoryEngine
from config.settings import CONFIG

class TestResponseGenerator(unittest.TestCase):
    def setUp(self):
        self.neo4j = Neo4jConnector(CONFIG["NEO4J_URI"], CONFIG["NEO4J_USER"], CONFIG["NEO4J_PASS"])
        self.memory_engine = MemoryEngine(self.neo4j)
        self.response_gen = ResponseGenerator(self.memory_engine, self.neo4j)

    def test_generate_response_with_memory(self):
        text = "I am happy"
        self.memory_engine.store_memory(text, "happy")
        response = self.response_gen.generate("emotion", text)
        self.assertIn("I recall", response)

if __name__ == "__main__":
    unittest.main()