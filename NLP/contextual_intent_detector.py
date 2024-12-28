import logging
from typing import Dict, List
from core.memory_engine import MemoryEngine

# Configure logging
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class ContextualIntentDetector:
    def __init__(self, memory_engine: MemoryEngine):
        """
        Initialize the ContextualIntentDetector with memory integration for context-aware intent detection.

        :param memory_engine: An instance of MemoryEngine for memory-based context analysis.
        """
        self.memory_engine = memory_engine
        self.keywords = {
            "greeting": ["hello", "hi", "hey", "good morning", "morning", "good evening"],
            "negation": ["i don't", "i disagree", "not really", "never mind", "i refuse"],
            "confirmation": ["yes", "correct", "right", "of course", "sure", "yeah"],
            "emotion_positive": ["happy", "joyful", "excited", "optimistic", "grateful"],
            "emotion_negative": ["sad", "angry", "frustrated", "lonely", "upset"],
            "ethical": ["virtue", "justice", "morality", "values", "is it right"],
            "thematic": ["faith", "hope", "love", "truth", "redemption", "purpose"],
        }

    def detect_intent(self, text: str) -> str:
        """
        Detect the intent from the given text using keyword matching and memory context.

        :param text: The text to analyze for intent.
        :return: The detected intent or 'unknown' if no intent matches.
        """
        try:
            text_lower = text.lower().strip()

            # Initialize scoring for all intents
            intent_scores: Dict[str, int] = {intent: 0 for intent in self.keywords}

            # Score based on keyword matches
            for intent, words in self.keywords.items():
                for word in words:
                    if word in text_lower:
                        intent_scores[intent] += 1

            # Incorporate memory context
            memory = self.memory_engine.search_memory(text)
            if memory:
                logger.info(f"[MEMORY CONTEXT] Found memory: {memory['text']} for input: '{text}'")
                for intent, words in self.keywords.items():
                    if any(word in memory['text'] for word in words):
                        intent_scores[intent] += 2  # Higher weight for memory matches

            # Determine the best matching intent
            best_intent = max(intent_scores, key=intent_scores.get)

            # Fallback if no significant score is found
            if intent_scores[best_intent] == 0:
                logger.info(f"[INTENT DETECTION] No intent detected for text: '{text}'")
                return "unknown"

            logger.info(f"[INTENT DETECTION] Detected intent: {best_intent} for text: '{text}'")
            return best_intent
        except Exception as e:
            logger.error(f"[INTENT DETECTION ERROR] Error detecting intent for text: '{text}': {e}", exc_info=True)
            return "unknown"
