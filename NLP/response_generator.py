# response_generator.py - Dynamic Responses

import random
import logging
from typing import Dict, List

# Configure logging
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

from NLP.contextual_intent_detector import ContextualIntentDetector

class ResponseGenerator:
    
    def __init__(self, memory_engine, neo4j_connector):
        """
        Initialize the ResponseGenerator with memory engine and Neo4j connector.

        :param memory_engine: An instance for managing memories.
        :param neo4j_connector: An instance of Neo4jConnector for database operations.
        """
        self.memory_engine = memory_engine
        self.neo4j_connector = neo4j_connector
        self.intent_detector = ContextualIntentDetector(neo4j_connector)

    def generate_response(self, memory: Dict) -> str:
        """
        Generate a dynamic response based on the memory data and detected intent.

        :param memory: A dictionary containing memory information including text and possibly emotions.
        :return: A string response tailored to the memory context.

        :raises KeyError: If required keys are missing from the memory dictionary.
        """
        try:
            # Detect emotions if not explicitly given
            if "emotions" not in memory or memory["emotions"] == ["neutral"]:
                detected_intent = self.intent_detector.detect_intent(memory["text"])

                # Apply Emotional Context
                emotions = ["happy"] if detected_intent == "emotion" else ["neutral"]
                memory["emotions"] = emotions
                logger.info(f"[EMOTION DETECTION] Detected emotions: {emotions} for text: {memory['text'][:50]}{'...' if len(memory['text']) > 50 else ''}")

            # Thought Generators
            thought_variations: List[str] = [
                f"Thinking about '{memory['text']}' brings emotions of {', '.join(memory['emotions'])}.",
                f"Reflecting on '{memory['text']}', I sense {', '.join(memory['emotions'])}.",
            ]
            context_variations: List[str] = [
                "Would you like to expand on this?",
                "Shall we reflect further?",
                "Is this still important to you?",
            ]

            final_response = f"{random.choice(thought_variations)} {random.choice(context_variations)}"
            logger.info(f"[GENERATED RESPONSE] {final_response[:100]}{'...' if len(final_response) > 100 else ''}")
            return final_response

        except KeyError as ke:
            logger.error(f"[RESPONSE GENERATION ERROR] Missing key in memory dict: {ke}")
            return "I'm having trouble processing that memory. Please try again."
        except Exception as e:
            logger.error(f"[RESPONSE GENERATION ERROR] {e}", exc_info=True)
            return "An unexpected error occurred while generating a response. Please try again."