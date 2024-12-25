from typing import Optional
from venv import logger
from core.conversation_engine import ConversationEngine

class CollaborativeLearning:
    def __init__(self, conversation_engine: ConversationEngine):
        self.conversation_engine = conversation_engine

    def detect_doubt(self, thought: str) -> bool:
        """
        Detect doubt or uncertainty in a thought.
        """
        return "?" in thought or "uncertain" in thought.lower()

    def generate_query(self, thought: str) -> Optional[str]:
        """
        Generate a query for user input if doubt is detected.
        """
        if self.detect_doubt(thought):
            return f"I'm unsure about '{thought}'. Can you clarify?"
        return None

    def handle_user_feedback(self, feedback: str):
        """
        Process user feedback to refine knowledge or behavior.
        """
        logger.info(f"[COLLABORATIVE LEARNING] User feedback received: {feedback}")
        self.conversation_engine.process_feedback(feedback)
