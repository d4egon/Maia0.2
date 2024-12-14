# Filename: tests/test_intent_detector.py

import sys, os, unittest
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from NLP.contextual_intent_detector import ContextualIntentDetector
from core.neo4j_connector import Neo4jConnector
from config.settings import CONFIG

class TestIntentDetector(unittest.TestCase):
    def setUp(self):
        self.neo4j = Neo4jConnector(CONFIG["NEO4J_URI"], CONFIG["NEO4J_USER"], CONFIG["NEO4J_PASS"])
        self.intent_detector = ContextualIntentDetector(self.neo4j)

    def test_greeting_intent(self):
        text = "Hello there!"
        intent = self.intent_detector.detect_intent(text)
        self.assertEqual(intent, "greeting")

    def test_unknown_intent(self):
        text = "random words that make no sense"
        intent = self.intent_detector.detect_intent(text)
        self.assertEqual(intent, "unknown")

if __name__ == "__main__":
    unittest.main()