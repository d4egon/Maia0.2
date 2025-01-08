from NLP.response_generator import ResponseGenerator
from core.context_search import ContextSearchEngine
from core.memory_engine import MemoryEngine
from core.collaborative_learning import CollaborativeLearning
from core.semantic_builder import SemanticBuilder
from sentence_transformers import SentenceTransformer, InputExample, losses # type: ignore
from torch.utils.data import DataLoader
from typing import List
import logging
import os


# Configure logging
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class ConversationEngine:
    def __init__(self, memory_engine: MemoryEngine, response_generator: ResponseGenerator,
                 context_search: ContextSearchEngine):
        """
        Initialize the ConversationEngine with necessary components and model for continuous learning.

        :param memory_engine: Handles memory operations.
        :param response_generator: Generates responses based on input.
        :param context_search: Searches for relevant context from past interactions.
        """
        self.memory_engine = memory_engine
        self.response_generator = response_generator
        self.context_search = context_search
        self.collaborative_learning = CollaborativeLearning(self)
        self.semantic_builder = SemanticBuilder(memory_engine.db)
        self.model = SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')
        
        # Save initial model state
        model_directory = os.path.join(os.getcwd(), "model_checkpoint")
        if not os.path.exists(model_directory):
            os.makedirs(model_directory)
        self.model.save(model_directory)
        logger.info(f"[MODEL INIT] Initial model state saved to {model_directory}")

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
                response = self.response_generator.generate_response(memory, user_input)
                logger.info(f"[MEMORY RESPONSE] {response}")
                return response

            # Step 2: Contextual Search
            context_result = self.context_search.search_related(user_input)
            if context_result:
                response = self.response_generator.generate_response(context_result, user_input)
                logger.info(f"[CONTEXTUAL RESPONSE] {response}")
                return response

            # Step 3: Semantic Analysis
            semantic_links = self.semantic_builder.infer_relationships(user_input, "past conversations")
            if semantic_links:
                self.memory_engine.store_memory(user_input, ["semantic"], {"semantic_links": semantic_links})
                related_memories = self.memory_engine.search_by_semantic_links(semantic_links)
                if related_memories:
                    response = self.response_generator.generate_response(related_memories, user_input)
                    logger.info(f"[SEMANTIC RESPONSE] {response}")
                    return response

            # Step 4: Thought Generation with Collaborative Doubt Handling
            def process_thought(input_text):
                from core.thought_engine import ThoughtEngine  # Local import
                thought_engine = ThoughtEngine(self.memory_engine.db)  # Assuming db is available
                generated_thought = thought_engine.reflect(input_text)
                if generated_thought:
                    self.memory_engine.store_memory(user_input, ["reflective"])
                    response = self.response_generator.generate_response(generated_thought, user_input)
                    logger.info(f"[THOUGHT RESPONSE] {response}")
                    return response
                return None

            thought_response = process_thought(user_input)
            if thought_response:
                return thought_response

            # Step 5: Fallback Response with Semantic Exploration
            fallback_response = self._generate_fallback_response(user_input)
            logger.warning(f"[FALLBACK RESPONSE] {fallback_response}")
            return fallback_response

        except Exception as e:
            logger.error(f"[PROCESS INPUT ERROR] {e}", exc_info=True)
            return "Sorry, I encountered an error. Please try again."

    def _generate_fallback_response(self, user_input: str) -> str:
        """
        Generate a fallback response using semantic exploration when no direct match is found.

        :param user_input: The user's query to explore.
        :return: A fallback response string.
        """
        semantic_exploration = self.semantic_builder.detect_narrative_shifts()
        if semantic_exploration:
            response = f"I couldn't find a direct match for your query, but I've noticed recent shifts in our conversation: {', '.join(semantic_exploration)}. Would you like to explore these themes?"
        else:
            response = "I'm sorry, I couldn't find anything related to your query. Can you provide more context or ask in a different way?"
        return response

    def process_feedback(self, feedback: str):
        """
        Process user feedback to refine M.A.I.A.'s knowledge and responses.
        """
        logger.info(f"[FEEDBACK PROCESSING] Received feedback: {feedback}")
        self.memory_engine.store_feedback(feedback)
        
        # Use feedback for semantic analysis
        feedback_analysis = self.semantic_builder.infer_relationships(feedback, "past feedback")
        if feedback_analysis:
            logger.info(f"[FEEDBACK ANALYSIS] {feedback_analysis}")
            self.memory_engine.update_with_feedback(feedback, feedback_analysis)

        logger.info("[FEEDBACK PROCESSING] Feedback stored and analyzed successfully.")

    def update_conversation_model(self, new_conversations: List[str]):
        """
        Update or fine-tune the NLP model with new conversation data.

        :param new_conversations: List of new conversations to learn from.
        """
        try:
            # Prepare training examples
            train_examples = []
            for i in range(len(new_conversations) - 1):  # Create pairs for similarity training
                train_examples.append(InputExample(texts=[new_conversations[i], new_conversations[i+1]], label=0.8))  # Assuming 0.8 similarity
            
            # DataLoader for batching
            train_dataloader = DataLoader(train_examples, shuffle=True, batch_size=16)
            
            # Loss function
            train_loss = losses.CosineSimilarityLoss(self.model)

            # Training loop
            self.model.fit(
                train_objectives=[(train_dataloader, train_loss)],
                epochs=1,  # You might want to adjust this based on how much you want to update per session
                warmup_steps=100,
                output_path="model_checkpoint",  # Save after each update
                show_progress_bar=True
            )

            logger.info(f"[MODEL UPDATE] Model updated with {len(new_conversations)} new inputs")
            self.memory_engine.store_bulk_memories(new_conversations, ["learning"])
        except Exception as e:
            logger.error(f"[MODEL UPDATE ERROR] {e}", exc_info=True)