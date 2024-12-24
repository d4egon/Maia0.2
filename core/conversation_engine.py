class ConversationEngine:
    def __init__(self, memory_engine: MemoryEngine, response_generator: ResponseGenerator, 
                 thought_engine: ThoughtEngine, context_search: ContextSearchEngine, collaborative_learning: CollaborativeLearning):
        """
        Initialize the ConversationEngine with necessary components.

        :param memory_engine: Handles memory operations.
        :param response_generator: Generates responses based on input.
        :param thought_engine: Processes thoughts or generates new content.
        :param context_search: Searches for relevant context from past interactions.
        :param collaborative_learning: Handles doubt detection and user collaboration.
        """
        self.memory_engine = memory_engine
        self.response_generator = response_generator
        self.thought_engine = thought_engine
        self.context_search = context_search
        self.collaborative_learning = collaborative_learning

    def process_user_input(self, user_input: str) -> str:
        """
        Process user input through a series of steps to generate a response.

        :param user_input: The input from the user to process.
        :return: A string response based on the processed input.
        """
        logger.info(f"[USER INPUT RECEIVED] {user_input}")

        try:
            # Step 1: Memory Search
            memory = self.memory_engine.search_memory(user_input)
            if memory:
                response = self.response_generator.generate_response(memory)
                logger.info(f"[MEMORY RESPONSE] {response}")
                return response

            # Step 2: Contextual Search
            context_result = self.context_search.search_related(user_input)
            if context_result:
                response = self.response_generator.generate_response(context_result)
                logger.info(f"[CONTEXTUAL RESPONSE] {response}")
                return response

            # Step 3: Thought Generation with Collaborative Doubt Handling
            generated_thought = self.thought_engine.reflect(user_input)
            if generated_thought:
                self.memory_engine.store_memory(user_input, ["reflective"])
                doubt_query = self.collaborative_learning.generate_query(generated_thought)
                if doubt_query:
                    logger.info(f"[DOUBT QUERY] {doubt_query}")
                    return doubt_query  # Return the question to the user
                response = self.response_generator.generate_response(generated_thought)
                logger.info(f"[THOUGHT RESPONSE] {response}")
                return response

            # Step 4: Fallback Response
            fallback_response = {"response": "I'm sorry, I couldn't find anything related to your query."}
            logger.warning(f"[FALLBACK RESPONSE] {fallback_response['response']}")
            return fallback_response['response']

        except Exception as e:
            logger.error(f"[PROCESS INPUT ERROR] {e}", exc_info=True)
            return "Sorry, I encountered an error. Please try again."

    def process_feedback(self, feedback: str):
        """
        Process user feedback to refine M.A.I.A.'s knowledge and responses.
        """
        logger.info(f"[FEEDBACK PROCESSING] Received feedback: {feedback}")
        self.memory_engine.store_feedback(feedback)
        logger.info("[FEEDBACK PROCESSING] Feedback stored successfully.")
