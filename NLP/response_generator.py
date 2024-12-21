# response_generator.py - Dynamic Responses

import random
import logging

logger = logging.getLogger(__name__)

from NLP.contextual_intent_detector import ContextualIntentDetector

class ResponseGenerator:
    
    def __init__(self, memory_engine, neo4j_connector):
        self.memory_engine = memory_engine
        self.neo4j_connector = neo4j_connector
        self.intent_detector = ContextualIntentDetector(neo4j_connector)

    def generate_response(self, memory):
        # Detect emotions if not explicitly given
        if "emotions" not in memory or memory["emotions"] == ["neutral"]:
            detected_intent = self.intent_detector.detect_intent(memory["text"])

            # Apply Emotional Context
            emotions = ["happy"] if detected_intent == "emotion" else ["neutral"]
            memory["emotions"] = emotions

        # Thought Generators
        thought_variations = [
            f"Thinking about '{memory['text']}' brings emotions of {', '.join(memory['emotions'])}.",
            f"Reflecting on '{memory['text']}', I sense {', '.join(memory['emotions'])}.",
        ]
        context_variations = [
            "Would you like to expand on this?",
            "Shall we reflect further?",
            "Is this still important to you?",
        ]

        final_response = f"{random.choice(thought_variations)} {random.choice(context_variations)}"
        logger.debug(f"[GENERATED RESPONSE] {final_response}")
        return final_response
