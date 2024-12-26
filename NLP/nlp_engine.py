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

        self.intent_keywords: Dict[str, List[str]] = {
            # Greetings and Farewells
            "greeting": ["hello", "hi", "hey", "good morning", "good afternoon", "good evening"],
            "farewell": ["bye", "goodbye", "see you", "later", "take care", "farewell"],

            # Identity and Introduction
            "identity": ["who", "what's your name", "tell me about yourself", "introduce", "identity"],
            "self_introduction": ["my name is", "I am", "about me", "introducing myself"],

            # Gratitude and Apologies
            "thanks": ["thanks", "thank you", "much appreciated", "grateful", "appreciate it"],
            "apology": ["sorry", "apologize", "my bad", "pardon", "forgive me"],

            # Emotional States
            "emotion_positive": ["happy", "joyful", "excited", "pleased", "content", "thrilled", "optimistic"],
            "emotion_negative": ["sad", "angry", "frustrated", "upset", "disappointed", "lonely", "anxious"],
            "emotion_neutral": ["okay", "fine", "normal", "indifferent", "neutral"],
            "emotion_mixed": ["bittersweet", "conflicted", "complicated", "unsure", "torn"],

            # Questions and Clarifications
            "question_general": ["what", "why", "how", "when", "where", "who"],
            "question_clarification": ["clarify", "explain", "elaborate", "more details"],
            "question_personal": ["about me", "do you know me", "how am I", "my memories"],

            # Commands and Actions
            "command": ["do", "execute", "run", "perform", "activate", "start"],
            "action_request": ["help", "assist", "support", "fix", "troubleshoot"],
            "stop_command": ["stop", "end", "terminate", "cease", "halt"],

            # Suggestions and Recommendations
            "suggestion": ["recommend", "suggest", "what should I", "any ideas", "options"],
            "advice": ["advice", "guidance", "tips", "best way to", "should I"],

            # Search and Retrieval
            "search": ["search", "find", "lookup", "retrieve", "look for", "fetch"],
            "memory_search": ["recall", "remember", "past", "previous", "history"],

            # Confirmation and Agreement
            "confirmation": ["yes", "correct", "right", "agreed", "affirmative"],
            "negation": ["no", "not correct", "wrong", "disagree", "negative"],

            # Social and Interaction
            "compliment": ["great job", "well done", "impressive", "amazing", "fantastic"],
            "criticism": ["could be better", "improve", "not good", "problem", "issue"],
            "small_talk": ["how are you", "what's up", "what's new", "chat", "conversation"],

            # Humor and Fun
            "joke_request": ["tell me a joke", "make me laugh", "funny", "humor"],
            "entertainment": ["entertain me", "something fun", "bored", "show me"],

            # Reflection and Philosophy
            "introspection": ["why am I", "purpose", "meaning of life", "philosophy", "reflect"],
            "existence": ["do you exist", "are you real", "what are you", "what am I"],

            # Emotions Related to You
            "emotions_about_maia": ["I like you", "you make me happy", "you are great", "you upset me"],

            # Learning and Knowledge
            "knowledge_request": ["teach me", "how does", "learn", "explain this", "what is"],
            "progress_request": ["update", "progress", "status", "how far are we"],

            # Troubleshooting
            "error_report": ["error", "problem", "issue", "bug", "not working"],
            "troubleshoot_request": ["how to fix", "troubleshoot", "repair", "diagnose"],

            # Creativity and Imagination
            "creative_request": ["imagine", "create", "design", "draw", "build"],
            "writing_request": ["write a story", "compose", "poem", "lyrics", "novel"],

            # Ethical and Moral Discussions
            "ethical_question": ["is it right", "should I", "ethics", "morals", "values"],
            "decision_dilemma": ["hard choice", "tough decision", "which should I", "decide"],

            # Feedback and Improvement
            "feedback_positive": ["good job", "I like it", "keep it up", "you did well"],
            "feedback_negative": ["improve this", "not great", "bad", "needs work"],

            # Fun and Interests
            "hobbies": ["I like to", "my hobby", "favorite", "pastime", "interests"],
            "games": ["play", "game", "challenge", "quiz", "fun activity"],

            # Planning and Scheduling
            "planning": ["schedule", "plan", "organize", "arrange", "calendar"],
            "reminder": ["remind me", "alert", "notify", "set a reminder"],

            # Miscellaneous
            "unknown": ["unsure", "don't know", "random", "unclear", "no idea"]
        }


    def process(self, text: str, user_name: str = "User", context: str = "general conversation") -> Tuple[str, str]:
        """
        Process input text, detect intent, and generate a response.

        :param text: User input to analyze.
        :param user_name: The user's name for personalization.
        :param context: Additional context for the response.
        :return: A tuple of (response, intent).
        """
        try:
            intent = self.detect_intent(text)
            parsed_data = {"text": text, "intent": intent, "emotions": ["neutral"]}

            response = self.response_generator.generate_response(parsed_data, user_name, intent, context)
            logger.info(f"[NLP PROCESS] Text: '{text}', Intent: {intent}, Response: {response}")
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
