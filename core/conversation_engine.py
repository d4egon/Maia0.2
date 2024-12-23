# conversation_engine.py - Fully Dynamic

import logging
from typing import Dict, List, Any
from core.memory_engine import MemoryEngine
from NLP.response_generator import ResponseGenerator
from core.thought_engine import ThoughtEngine
from context_search import ContextSearch

# Configure logging
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class ConversationEngine:
    def __init__(self, memory_engine: MemoryEngine, response_generator: ResponseGenerator, 
                 thought_engine: ThoughtEngine, context_search: ContextSearch):
        """
        Initialize the ConversationEngine with necessary components.

        :param memory_engine: Handles memory operations.
        :param response_generator: Generates responses based on input.
        :param thought_engine: Processes thoughts or generates new content.
        :param context_search: Searches for relevant context from past interactions.
        """
        self.memory_engine = memory_engine
        self.response_generator = response_generator
        self.thought_engine = thought_engine
        self.context_search = context_search

    def process_user_input(self, user_input: str) -> str:
        """
        Process user input through a series of steps to generate a response.

        :param user_input: The input from the user to process.
        :return: A string response based on the processed input.
        """
        logger.info(f"[USER INPUT RECEIVED] {user_input}")

        try:
            # Step 1: Contextual Memory Search
            memory = self.memory_engine.search_memory(user_input)
            if memory:
                response = self.response_generator.generate_response(memory)
                logger.info(f"[MEMORY RESPONSE] {response}")
                return response

            # Step 2: Contextual Search for Similar Memories
            context_result = self.context_search.search_related(user_input)
            if context_result:
                response = self.response_generator.generate_response(context_result)
                logger.info(f"[CONTEXTUAL RESPONSE] {response}")
                return response

            # Step 3: Thought Generation for New Queries
            generated_thought = self.thought_engine.generate_thought(user_input)
            if generated_thought:
                self.memory_engine.store_memory(user_input, ["reflective"])
                response = self.response_generator.generate_response(generated_thought)
                logger.info(f"[THOUGHT RESPONSE] {response}")
                return response

            # Step 4: Fallback Response (Suggest Memory Storage)
            fallback_response = self.memory_engine.suggest_memory_storage(user_input)
            logger.warning(f"[FALLBACK RESPONSE] {fallback_response['response']}")
            return fallback_response['response']

        except Exception as e:
            logger.error(f"[PROCESS INPUT ERROR] An error occurred while processing user input: {e}", exc_info=True)
            return "Sorry, I encountered an error. Please try again."

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        # Here, you might want to add cleanup operations or ensure all components are closed or saved if needed
        pass