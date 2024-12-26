import random
import logging
from typing import Dict, List
from NLP.contextual_intent_detector import ContextualIntentDetector
from core.neo4j_connector import Neo4jConnector
from core.memory_engine import MemoryEngine  # Assuming this is the correct import for your MemoryEngine

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
        :raises KeyError: If required keys are missing from the memory dictionary.

        This method crafts responses with greater engagement, using emotional detection, 
        personalized greetings, and context-aware statements.
        """
        try:
            # Detect or update emotions based on the input
            if "emotions" not in memory or not memory["emotions"]:
                detected_emotions = self.memory_engine.search_memory(memory["text"])
                if detected_emotions:
                    memory["emotions"] = detected_emotions.get("emotions", ["neutral"])
                else:
                    # Use intent to infer emotion if no stored data
                    emotion_intent = self.intent_detector.detect_intent(memory["text"])
                    memory["emotions"] = ["happy"] if emotion_intent == "emotion_positive" else ["neutral"]
                logger.info(f"[EMOTION DETECTION] Detected or used default emotions: {memory['emotions']} for text: {memory['text'][:50]}{'...' if len(memory['text']) > 50 else ''}")

            # Personalized Greetings and Reflections
            greeting_variations = [
                f"Hello {user_name}, I sense your {', '.join(memory['emotions'])} feelings when thinking about '{memory['text']}'.",
                f"{user_name}, your thoughts on '{memory['text']}' evoke a sense of {', '.join(memory['emotions'])}."
            ]

            # Deep Reflections or Questions based on Intent and Context
            reflective_questions = {
                "greeting": ["How's your day going?", "What brings you here today?"],
                "negation": ["I understand you're not in agreement. Would you like to discuss something else?", "What would you rather talk about?"],
                "confirmation": ["Great to hear we're on the same page. What's next?", "I'm glad we agree. Any further thoughts?"],
                "emotion": [f"I see you're feeling {memory['emotions'][0]}. Want to share more?", "Your emotional state seems to be {memory['emotions'][0]}. How can I assist?"],
                "default": ["Tell me more about this, " + user_name, "Is there anything specific you want to discuss?"]
            }

            # Choose the appropriate reflection or question based on intent
            selected_question = random.choice(reflective_questions.get(intent, reflective_questions["default"]))
            
            # Combine greeting with context-aware questions
            final_response = f"{random.choice(greeting_variations)} {selected_question} In the context of {context}, what are your thoughts?"
            
            logger.info(f"[GENERATED RESPONSE] {final_response[:100]}{'...' if len(final_response) > 100 else ''}")
            return final_response

        except KeyError as ke:
            logger.error(f"[RESPONSE GENERATION ERROR] Missing key in memory dict: {ke}")
            return f"I'm having trouble processing that thought, {user_name}. Please try again."
        except Exception as e:
            logger.error(f"[RESPONSE GENERATION ERROR] {e}", exc_info=True)
            return f"Something unexpected happened while crafting your response, {user_name}. Please try again."