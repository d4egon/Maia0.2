import logging
from typing import Dict, List, Tuple
from NLP.sentence_parser import SentenceParser
from NLP.tokenizer import Tokenizer

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
        self.tokenizer = Tokenizer()
        self.sentence_parser = SentenceParser()

        self.intent_keywords: Dict[str, List[str]] = {
            # Ethical Discussions
            "ethical_question": ["is it right", "should I", "ethics", "morals", "values"],
            "decision_dilemma": ["hard choice", "tough decision", "which should I", "decide"],
        }

    def process(self, text: str, user_name: str = "User", context: str = "general conversation") -> Tuple[str, str]:
        """
        Process input text, detect intent, analyze emotions, and generate a response.

        :param text: User input to analyze.
        :param user_name: The user's name for personalization.
        :param context: Additional context for the response.
        :return: A tuple of (response, intent).
        """
        try:
            tokens = self.tokenizer.tokenize(text)
            parsed_data = self.sentence_parser.parse(tokens)

            intent = self.detect_intent(text)
            emotions = self.analyze_emotions(tokens)

            context_data = {"text": text, "tokens": tokens, "parsed": parsed_data, "emotions": emotions}
            response = self.response_generator.generate_response(context_data, user_name, intent, context)

            logger.info(f"[NLP PROCESS] Text: '{text}', Intent: {intent}, Emotions: {emotions}, Response: {response}")
            return response, intent

        except Exception as e:
            logger.error(f"[NLP PROCESS ERROR] {e}", exc_info=True)
            return "I'm sorry, I encountered an error.", "error"

    def detect_intent(self, text: str) -> str:
        """
        Detect intent based on keywords.

        :param text: The text to analyze.
        :return: The detected intent or 'unknown' if no match.
        """
        try:
            words = text.lower().split()
            for intent, keywords in self.intent_keywords.items():
                if any(keyword in words for keyword in keywords):
                    logger.info(f"[INTENT DETECTED] Text: {text}, Intent: {intent}")
                    return intent

            logger.info(f"[INTENT DETECTION] No intent matched for text: {text}")
            return "unknown"
        except Exception as e:
            logger.error(f"[INTENT DETECTION ERROR] {e}", exc_info=True)
            return "unknown"

    def analyze_emotions(self, tokens: List[Dict[str, str]]) -> List[str]:
        """
        Analyze emotions based on token types and predefined emotional keywords.

        :param tokens: Tokenized input.
        :return: A list of detected emotions.
        """
        emotion_keywords = {
            "positive": ["happy", "joyful", "grateful", "optimistic"],
            "negative": ["sad", "angry", "frustrated", "lonely"],
            "neutral": ["okay", "fine", "indifferent", "neutral"]
        }

        emotions = []
        for token in tokens:
            if token["type"] == "word" and token["value"].lower() in emotion_keywords:
                for emotion, keywords in emotion_keywords.items():
                    if token["value"].lower() in keywords:
                        emotions.append(emotion)
                        break

        logger.info(f"[EMOTION ANALYSIS] Detected emotions: {emotions}")
        return emotions if emotions else ["neutral"]
