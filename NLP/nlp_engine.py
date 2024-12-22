# Filename: NLP/nlp_engine.py

import logging
from typing import Dict, List, Tuple

# Configure logging
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class NLP:
    def __init__(self, memory_engine, response_generator, neo4j_connector):
        """
        Initialize the NLP engine with necessary components.

        :param memory_engine: An instance of MemoryEngine for memory operations.
        :param response_generator: An instance for generating responses.
        :param neo4j_connector: An instance of Neo4jConnector for database operations.
        """
        self.memory_engine = memory_engine
        self.response_generator = response_generator
        self.neo4j_connector = neo4j_connector

        # Intent Keyword Storage (can be expanded dynamically)
        self.intent_keywords: Dict[str, List[str]] = {
            "greeting": ["hello", "hi", "good morning", "good evening"],
            "identity": ["who", "what's your name", "tell me about yourself"],
            "exit": ["bye", "goodbye", "see you"],
            "thanks": ["thanks", "thank you", "appreciate"],
            "apology": ["sorry", "my bad", "apologies"],
            "help": ["help", "assist", "support"],
            "question": ["what", "why", "how", "when", "where"],
            "emotion_positive": ["happy", "joyful", "excited", "pleased"],
            "emotion_negative": ["sad", "angry", "frustrated", "upset"],
            "command": ["do", "execute", "run"],
            "search": ["search", "find", "lookup"],
        }

    def process(self, text: str) -> Tuple[str, str]:
        """
        Process the input text, detect intent, and generate a response.

        :param text: User input text to process.
        :return: A tuple of (response, intent).
        """
        try:
            intent = self.detect_intent(text)
            parsed_data = {"text": text, "intent": intent}

            response = self.response_generator.generate(parsed_data, intent, text)
            logger.info(f"[NLP PROCESS] Text: '{text}', Detected Intent: {intent}, Response: {response[:50]}{'...' if len(response) > 50 else ''}")
            return response, intent
        except Exception as e:
            logger.error(f"[NLP PROCESS ERROR] {e}", exc_info=True)
            return "An error occurred while processing your request.", "error"

    def detect_intent(self, text: str) -> str:
        """
        Detect intent based on keywords, learning dynamically.

        :param text: The text to analyze for intent.
        :return: The detected intent or 'unknown' if no match found.
        """
        try:
            words = text.lower().split()

            # Find matching intent
            for intent, keywords in self.intent_keywords.items():
                if any(word in words for word in keywords):
                    logger.info(f"[INTENT DETECTED] Text: {text}, Intent: {intent}")
                    return intent

            logger.info(f"[INTENT DETECTION] No intent matched for text: {text}")
            return "unknown"
        except Exception as e:
            logger.error(f"[INTENT DETECTION ERROR] {e}", exc_info=True)
            return "unknown"

    def handle_intent_feedback(self, user_input: str, detected_intent: str):
        """
        Handle user feedback on incorrect intents.

        :param user_input: User's feedback on the detected intent.
        :param detected_intent: The intent that was initially detected.
        """
        try:
            if user_input.lower() == "no":
                logger.info(f"[FEEDBACK] User disagreed with intent: {detected_intent}")
                print("Maia: Oh, you disagree. What would be a better meaning?")
                corrected_intent = input("You: ").strip().lower()

                if corrected_intent:
                    self.add_new_intent(corrected_intent, [detected_intent])
                    print(f"Maia: Thank you! I've learned '{corrected_intent}' as a new meaning.")

            elif user_input.lower() == "yes":
                logger.info(f"[FEEDBACK] User confirmed intent: {detected_intent}")
                print("Maia: Great! I’ll remember that.")
        except Exception as e:
            logger.error(f"[FEEDBACK HANDLING ERROR] {e}", exc_info=True)

    def add_new_intent(self, intent: str, keywords: List[str]):
        """
        Add a new intent and associated keywords dynamically.

        :param intent: The name of the new intent.
        :param keywords: List of keywords associated with the new intent.
        """
        try:
            if intent not in self.intent_keywords:
                self.intent_keywords[intent] = keywords
                logger.info(f"[INTENT ADDED] New intent '{intent}' added with keywords: {keywords}")
            else:
                # Expand existing keywords
                current_keywords = self.intent_keywords[intent]
                updated_keywords = list(set(current_keywords + keywords))
                self.intent_keywords[intent] = updated_keywords
                logger.info(f"[INTENT UPDATED] Intent '{intent}' updated with keywords: {updated_keywords}")

            # Update the memory graph
            self.update_intent_in_neo4j(intent, keywords)
        except Exception as e:
            logger.error(f"[ADDING INTENT ERROR] {e}", exc_info=True)

    def update_intent_in_neo4j(self, intent: str, keywords: List[str]):
        """
        Update Neo4j with new intents and keywords.

        :param intent: The intent to update or add in Neo4j.
        :param keywords: List of keywords to associate with the intent in Neo4j.
        """
        try:
            query = """
            MERGE (i:Intent {name: $intent})
            FOREACH (kw IN $keywords | 
                MERGE (k:Keyword {name: kw}) 
                MERGE (i)-[:HAS_KEYWORD]->(k))
            """
            self.neo4j_connector.run_query(query, {"intent": intent, "keywords": keywords})
            logger.info(f"[NEO4J UPDATE] Updated intent '{intent}' with keywords: {keywords}")
        except Exception as e:
            logger.error(f"[NEO4J UPDATE ERROR] {e}", exc_info=True)