from typing import Optional
from venv import logger

class CollaborativeLearning:
    def __init__(self, conversation_engine):
        """
        Initialize CollaborativeLearning with a reference to the ConversationEngine.

        :param conversation_engine: An instance of ConversationEngine.
        """
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
        from core.conversation_engine import ConversationEngine  # Lazy import
        if isinstance(self.conversation_engine, ConversationEngine):
            logger.info(f"[COLLABORATIVE LEARNING] User feedback received: {feedback}")
            self.conversation_engine.process_feedback(feedback)

    def explore_ambiguity(self, thought: str):
        """
        Collaboratively explore ambiguous or unclear thoughts.
    
        :param thought: The ambiguous thought to explore.
        """
        if self.detect_doubt(thought):
            question = self.generate_query(thought)
            logger.info(f"[AMBIGUITY DETECTION] {question}")
            return question
        return "No ambiguity detected."
    
    def integrate_feedback_loop(self, feedback: str):
        """
        Integrate user feedback into a refinement loop.
    
        :param feedback: Feedback to integrate.
        """
        try:
            logger.info(f"[FEEDBACK INTEGRATION] Integrating feedback: {feedback}")
            refined_knowledge = self.conversation_engine.process_feedback(feedback)
            return refined_knowledge
        except Exception as e:
            logger.error(f"[FEEDBACK ERROR] {e}", exc_info=True)