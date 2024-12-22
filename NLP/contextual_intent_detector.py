import logging
from typing import Dict, List

# Configure logging
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class ContextualIntentDetector:
    def __init__(self, neo4j_connector):
        """
        Initialize the ContextualIntentDetector with a Neo4j connector for potential database queries.

        :param neo4j_connector: An instance of Neo4jConnector for database operations.
        """
        self.neo4j_connector = neo4j_connector
        self.keywords = {
            "greeting": ["hello", "hi", "hey", "good morning", "morning", "good evening"],
            "negation": ["i don't", "i disagree", "not really", "never mind", "i refuse"],
            "confirmation": ["yes", "correct", "right", "of course", "sure", "yeah"],
            "emotion": ["happy", "sad", "angry", "excited", "bored", "calm"]
        }

    def detect_intent(self, text: str) -> str:
        """
        Detect the intent from the given text using keyword matching.

        :param text: The text to analyze for intent.
        :return: The detected intent or 'unknown' if no intent matches.
        """
        try:
            text_lower = text.lower().strip()

            # Scoring system for intents
            intent_scores: Dict[str, int] = {intent: 0 for intent in self.keywords}

            # Check for keyword matches
            for intent, words in self.keywords.items():
                for word in words:
                    if word in text_lower:
                        intent_scores[intent] += 1

            # Find the best match or fallback to unknown
            best_intent = max(intent_scores, key=intent_scores.get)

            if intent_scores[best_intent] == 0:
                logger.info(f"[INTENT DETECTION] No intent detected for: '{text}'")
                return "unknown"

            # Avoid misclassifying short phrases as negation
            if best_intent == "negation" and len(text_lower.split()) < 3:
                logger.info(f"[INTENT DETECTION] Negation intent avoided due to short phrase for: '{text}'")
                return "unknown"

            logger.info(f"[INTENT DETECTION] Detected intent: {best_intent} for text: '{text}'")
            return best_intent
        except Exception as e:
            logger.error(f"[INTENT DETECTION ERROR] Error detecting intent for '{text}': {e}", exc_info=True)
            return "unknown"