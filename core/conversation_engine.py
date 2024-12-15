# Filename: /core/conversation_engine.py

import logging
from core.memory_engine import MemoryEngine
from core.response_generator import ResponseGenerator

# Initialize logging
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

class ConversationEngine:
    def __init__(self, memory_engine: MemoryEngine, response_generator: ResponseGenerator):
        self.memory_engine = memory_engine
        self.response_generator = response_generator

    def generate_conversation(self, user_input, context_limit=5):
        """
        Generate a dynamic conversation based on memory and emotional context.
        """
        try:
            logger.info(f"[CONVERSATION] Processing user input: '{user_input}'")

            # Retrieve context from memory
            relevant_memories = self.memory_engine.search_related_memories(user_input, context_limit)

            # Build context-aware prompt
            context_summary = self.build_context_summary(relevant_memories)
            response = self.response_generator.generate_response(user_input, context_summary)

            # Log the conversation
            self.memory_engine.store_memory(
                user_input, "user_input",
                additional_data={"source": "conversation"}
            )
            self.memory_engine.store_memory(
                response, "maia_response",
                additional_data={"context": context_summary, "type": "conversation"}
            )

            logger.info(f"[CONVERSATION] Response generated: '{response}'")
            return response

        except Exception as e:
            logger.error(f"[CONVERSATION FAILED] Error during conversation generation: {e}", exc_info=True)
            return "I'm sorry, something went wrong."

    def build_context_summary(self, memories):
        """
        Create a summarized context from related memories.
        """
        if not memories:
            return "No relevant context found."

        summary = "\n".join([f"Memory: {m['text']} (Emotion: {m['emotion']})" for m in memories])
        logger.debug(f"[CONTEXT SUMMARY] {summary}")
        return summary