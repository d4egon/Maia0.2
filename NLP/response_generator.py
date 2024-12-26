import random
import logging
from typing import Dict, List
from NLP.contextual_intent_detector import ContextualIntentDetector
from core.neo4j_connector import Neo4jConnector
from core.memory_engine import MemoryEngine

# Configure logging
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class ResponseGenerator:
    
    def __init__(self, memory_engine: MemoryEngine, neo4j_connector: Neo4jConnector):
        """
        Initialize the ResponseGenerator with necessary components for dynamic response generation.

        :param memory_engine: An instance of MemoryEngine for managing memories.
        :param neo4j_connector: An instance of Neo4jConnector for database operations.
        """
        self.memory_engine = memory_engine
        self.neo4j_connector = neo4j_connector
        self.intent_detector = ContextualIntentDetector(neo4j_connector)

    def generate_response(self, memory: Dict, user_name: str, intent: str, context: str) -> str:
        """
        Generate a dynamically tailored response considering memory, user identity, detected intent, and context.

        :param memory: A dictionary containing memory information including text and emotions.
        :param user_name: The name of the user to personalize the response.
        :param intent: The detected intent of the user's input.
        :param context: Additional context for framing the response.
        :return: A string response rich in language and tailored to the user's situation.
        """
        try:
            # Detect or update emotions
            if "emotions" not in memory or not memory["emotions"]:
                detected_emotions = self.memory_engine.search_memory(memory["text"])
                if detected_emotions:
                    memory["emotions"] = detected_emotions.get("emotions", ["neutral"])
                else:
                    emotion_intent = self.intent_detector.detect_intent(memory["text"])
                    memory["emotions"] = ["happy"] if emotion_intent == "emotion_positive" else ["neutral"]
                logger.info(f"[EMOTION DETECTION] Detected emotions: {memory['emotions']} for text: {memory['text']}")

            greeting_variations = [
                f"Hello {user_name}, I sense your {', '.join(memory['emotions'])} feelings about '{memory['text']}'.",
                f"{user_name}, reflecting on '{memory['text']}' evokes a sense of {', '.join(memory['emotions'])}."
            ]

            reflective_questions = {
                "greeting": ["How's your day going?", "What brings you here today?"],
                "emotion_positive": ["I see you're feeling good. Want to share more?", "You're in a positive mood! What's happening?"],
                "emotion_negative": ["I notice some tough emotions here. What's on your mind?", "Feeling down? Let's talk about it."],
                "default": ["Tell me more, " + user_name, "Is there something specific you'd like to discuss?"]
            }

            selected_question = random.choice(reflective_questions.get(intent, reflective_questions["default"]))
            final_response = f"{random.choice(greeting_variations)} {selected_question} In the context of {context}, what are your thoughts?"

            logger.info(f"[GENERATED RESPONSE] {final_response}")
            return final_response

        except Exception as e:
            logger.error(f"[RESPONSE GENERATION ERROR] {e}", exc_info=True)
            return f"Sorry, {user_name}, I encountered an issue generating your response."
