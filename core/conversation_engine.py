# conversation_engine.py - Fully Dynamic

import logging
from core.memory_engine import MemoryEngine
from NLP.response_generator import ResponseGenerator
from thought_engine import ThoughtEngine
from context_search import ContextSearch

logger = logging.getLogger(__name__)

class ConversationEngine:
    def __init__(self, memory_engine, response_generator, thought_engine, context_search):
        self.memory_engine = memory_engine
        self.response_generator = response_generator
        self.thought_engine = thought_engine
        self.context_search = context_search

    def process_user_input(self, user_input):
        logger.info(f"[USER INPUT RECEIVED] {user_input}")

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
        response = self.memory_engine.suggest_memory_storage(user_input)
        logger.warning(f"[FALLBACK RESPONSE] {response['response']}")
        return response['response']
