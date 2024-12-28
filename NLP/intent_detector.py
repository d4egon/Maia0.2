import logging
from typing import List, Dict
from core.memory_engine import MemoryEngine

# Configure logging
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class IntentDetector:
    def __init__(self, memory_engine: MemoryEngine):
        """
        Initialize the IntentDetector with a comprehensive list of intents, associated keywords,
        and memory integration for enhanced context.

        :param memory_engine: An instance of MemoryEngine to access stored memories.
        """
        self.memory_engine = memory_engine
        self.intents: Dict[str, List[str]] = {
            "greeting": ["hello", "hi", "hey", "greetings", "good morning", "good evening"],
            "identity": ["who", "what", "name", "you", "your purpose", "identity", "self", "origin"],
            "exit": ["bye", "exit", "quit", "goodbye", "see you later", "farewell"],
            "ethical_question": ["is it right", "should I", "ethics", "morals", "values", "virtue", "justice"],
            "thematic_query": ["meaning", "purpose", "faith", "hope", "redemption", "love", "truth"],
            "question": ["what", "why", "how", "when", "where", "which", "could", "do"],
            "confirmation": ["yes", "yeah", "sure", "okay", "indeed", "affirmative", "right", "correct"],
            "negation": ["no", "nope", "not", "never", "negative", "disagree", "wrong"],
        }

    def detect_intent(self, tokens: List[str]) -> str:
        """
        Detect the intent based on the presence of keywords in the tokenized text and memory relevance.

        :param tokens: List of tokens (words) to check against intents.
        :return: The detected intent or 'unknown' if no match found.
        """
        try:
            # First, match intents based on keywords
            detected_intent = "unknown"
            for intent, keywords in self.intents.items():
                if any(token.lower() in keywords for token in tokens):
                    detected_intent = intent
                    break

            # If no intent is matched, check related memories
            if detected_intent == "unknown":
                text = " ".join(tokens)
                memory = self.memory_engine.search_memory(text)
                if memory:
                    logger.info(f"[MEMORY CONTEXT] Found related memory: {memory['text']} for tokens: {tokens}")
                    if any(keyword in memory['text'] for keyword in self.intents["ethical_question"]):
                        detected_intent = "ethical_question"
                    elif any(keyword in memory['text'] for keyword in self.intents["thematic_query"]):
                        detected_intent = "thematic_query"

            logger.info(f"[INTENT DETECTION] Detected intent: {detected_intent} for tokens: {tokens}")
            return detected_intent
        except Exception as e:
            logger.error(f"[INTENT DETECTION ERROR] Error detecting intent for tokens: {tokens}: {e}", exc_info=True)
            return "unknown"
