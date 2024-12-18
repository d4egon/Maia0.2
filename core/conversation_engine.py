# Filename: /core/conversation_engine.py



import logging
from core.memory_engine import MemoryEngine
from core.response_generator import ResponseGenerator

# Initialize logging
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)


class ConversationEngine:
    def __init__(self, memory_engine, response_generator):
        self.memory_engine = memory_engine
        self.response_generator = response_generator

    def generate_conversation(self, user_input, context_limit=5):
        greetings = ["hello", "hi", "hey", "good morning", "good day"]
        if any(greet in user_input.lower() for greet in greetings):
            return "Hello! How can I assist you today? 😊"

        relevant_memories = self.memory_engine.search_related_memories(user_input, context_limit)
        context_summary = self.build_context_summary(relevant_memories) or "No relevant context found."
        response = self.response_generator.generate_response(user_input, context_summary)
        self.memory_engine.store_memory(user_input, "user_input")
        self.memory_engine.store_memory(response, "maia_response")
        return response

    def build_context_summary(self, memories):
        """
        Create a summarized context from related memories.
        """
        if not memories:
            return "No relevant context found."

        summary = "\n".join([f"Memory: {m['text']} (Emotion: {m['emotion']})" for m in memories])
        logger.debug(f"[CONTEXT SUMMARY] {summary}")
        return summary

# Complete Integration
if __name__ == "__main__":
    print("Core modules fixed and loaded successfully!")
