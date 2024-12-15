# Filename: /core/dream_engine.py

import logging
import random
from core.memory_engine import MemoryEngine
from core.context_search import ContextSearchEngine

# Initialize logging
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

class DreamEngine:
    def __init__(self, memory_engine: MemoryEngine, context_search: ContextSearchEngine):
        self.memory_engine = memory_engine
        self.context_search = context_search

    def generate_dream(self):
        """
        Create a symbolic dream by linking memories in abstract and emotional contexts.
        """
        try:
            logger.info("[DREAM] Generating a symbolic dream...")

            # Select random core memories as a dream seed
            seed_memories = self.select_random_memories()

            if not seed_memories:
                logger.warning("[DREAM] No memories found for dreaming.")
                return "A void of forgotten thoughts..."

            # Expand memories with related contexts
            dream_context = self.expand_memories(seed_memories)

            # Symbolic dream creation
            dream_narrative = self.create_dream_narrative(dream_context)

            # Store dream as a reflective memory
            self.memory_engine.store_memory(
                dream_narrative, "dream", additional_data={"type": "symbolic_dream"}
            )

            logger.info(f"[DREAM] Dream generated: {dream_narrative}")
            return dream_narrative

        except Exception as e:
            logger.error(f"[DREAM FAILED] {e}", exc_info=True)
            return "A fragmented dream, lost in time..."

    def select_random_memories(self, count=3):
        """
        Randomly select core memories as a starting point for the dream.
        """
        query = """
        MATCH (m:Memory)
        WHERE m.weight > 0
        RETURN m.text AS memory, m.emotion AS emotion, m.weight AS weight
        ORDER BY rand() LIMIT $count
        """
        results = self.memory_engine.db.run_query(query, {"count": count})
        logger.debug(f"[MEMORY SELECTION] Selected memories: {results}")
        return results

    def expand_memories(self, seed_memories):
        """
        Expand memories using context search and related links.
        """
        expanded_context = []

        for memory in seed_memories:
            related_contexts = self.context_search.find_contextual_links(
                memory_text=memory['memory']
            )
            expanded_context.extend(related_contexts)

        logger.debug(f"[MEMORY EXPANSION] Expanded contexts: {expanded_context}")
        return expanded_context

    def create_dream_narrative(self, memories):
        """
        Construct a symbolic dream narrative from memories.
        """
        if not memories:
            return "The dream is empty and silent."

        dream_fragments = [
            f"{m['memory']} ({m['emotion']})" for m in memories
        ]
        dream_narrative = " ".join(random.sample(dream_fragments, len(dream_fragments)))

        logger.debug(f"[DREAM NARRATIVE] Constructed: {dream_narrative}")
        return f"In a symbolic world: {dream_narrative}."