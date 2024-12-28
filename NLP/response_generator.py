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
        self.intent_detector = ContextualIntentDetector(memory_engine)

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
            # Retrieve relevant memories
            related_memory = self.memory_engine.search_memory(memory["text"])
            memory_text = related_memory["text"] if related_memory else "no related memory found"

            # Base response components
            base_greeting = f"Hello {user_name}, "
            emotion_phrase = f"I sense your {', '.join(memory.get('emotions', ['neutral']))} feelings. "
            memory_phrase = f"I recall something: '{memory_text}'. " if related_memory else "This seems new to me. "

            # Intent-specific responses
            intent_responses = {
                "greeting": ["How's your day going?", "What brings you here today?"],
                "ethical_question": [
                    "That's an important ethical question. Let's reflect on it together.",
                    "Morality often challenges us. What do you think about this situation?"
                ],
                "thematic_query": [
                    "Faith, hope, and love often guide our actions. What resonates with you most?",
                    "This reminds me of profound truths. Do you have a perspective to share?"
                ],
                "emotion_positive": ["I'm glad to see you're in good spirits! Want to share more?", "It's wonderful to feel joy. What sparked it?"],
                "emotion_negative": ["I'm here to listen if you're feeling down.", "Would you like to talk about what's bothering you?"],
                "unknown": ["Tell me more, so I can better understand.", "I'm intrigued by your thoughts. Please elaborate."],
            }

            # Build the response
            selected_response = random.choice(intent_responses.get(intent, ["Let's explore this further."]))
            final_response = f"{base_greeting}{emotion_phrase}{memory_phrase}{selected_response}"

            logger.info(f"[GENERATED RESPONSE] {final_response}")
            return final_response

        except Exception as e:
            logger.error(f"[RESPONSE GENERATION ERROR] {e}", exc_info=True)
            return f"Sorry, {user_name}, I encountered an issue generating your response."
