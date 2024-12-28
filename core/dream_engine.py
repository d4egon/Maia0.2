# Filename: /core/dream_engine.py

import logging
import random
from typing import List, Dict
from core.memory_engine import MemoryEngine
from core.context_search import ContextSearchEngine

# Configure logging
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class DreamEngine:
    def __init__(self, memory_engine: MemoryEngine, context_search: ContextSearchEngine):
        """
        Initialize the DreamEngine with memory and context search capabilities.

        :param memory_engine: An instance of MemoryEngine for memory operations.
        :param context_search: An instance of ContextSearchEngine for context-based searching.
        """
        self.memory_engine = memory_engine
        self.context_search = context_search

    def generate_dream(self) -> str:
        """
        Generate a symbolic dream by linking memories in abstract and emotional contexts.

        :return: A narrative describing the dream or an error message.
        """
        try:
            logger.info("[DREAM] Initiating dream generation...")

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

            logger.info(f"[DREAM] Dream generated: {dream_narrative[:100]}{'...' if len(dream_narrative) > 100 else ''}")
            return dream_narrative

        except Exception as e:
            logger.error(f"[DREAM FAILED] {e}", exc_info=True)
            return "A fragmented dream, lost in time..."

    def select_random_memories(self, count: int = 3) -> List[Dict]:
        """
        Randomly select core memories as a starting point for the dream.

        :param count: Number of memories to select.
        :return: List of dictionaries containing memory details.
        """
        query = """
        MATCH (m:Memory)
        WHERE m.weight > 0
        RETURN m.text AS memory, m.emotion AS emotion, m.weight AS weight
        ORDER BY rand() LIMIT $count
        """
        results = self.memory_engine.db.run_query(query, {"count": count})
        logger.debug(f"[MEMORY SELECTION] Selected {len(results)} memories.")
        return results

    def expand_memories(self, seed_memories: List[Dict]) -> List[Dict]:
        """
        Expand given memories using context search to find related links.

        :param seed_memories: List of dictionaries representing core memories.
        :return: List of dictionaries with expanded, related memories.
        """
        expanded_context = []
        for memory in seed_memories:
            try:
                related_contexts = self.context_search.find_contextual_links(memory_text=memory['memory'])
                expanded_context.extend(related_contexts)
            except Exception as e:
                logger.error(f"[CONTEXT EXPANSION ERROR] for memory {memory['memory']}: {e}")
        logger.debug(f"[MEMORY EXPANSION] Expanded to {len(expanded_context)} contexts.")
        return expanded_context

    def create_dream_narrative(self, memories: List[Dict]) -> str:
        """
        Construct a symbolic dream narrative from a list of memories.

        :param memories: List of memory dictionaries to weave into a narrative.
        :return: A string representing the dream narrative.
        """
        if not memories:
            return "The dream is empty and silent."

        dream_fragments = [
            f"{m['memory']} ({m['emotion']})" for m in memories if m.get('memory') and m.get('emotion')
        ]
        if not dream_fragments:
            return "A dream where words fail to describe..."

        dream_narrative = " ".join(random.sample(dream_fragments, len(dream_fragments)))

        logger.debug(f"[DREAM NARRATIVE] Constructed narrative with length: {len(dream_narrative)}")
        return f"In a symbolic world: {dream_narrative}."

    def weighted_dream_generation(self) -> str:
        """
        Generate a dream narrative with weighted importance for key themes.
    
        :return: Weighted dream narrative.
        """
        try:
            seed_memories = self.select_random_memories()
            weights = {memory["theme"]: memory["weight"] for memory in seed_memories}
            narrative = " ".join(f"{theme} ({weights[theme]})" for theme in weights)
            logger.info(f"[WEIGHTED DREAM] {narrative}")
            return narrative
        except Exception as e:
            logger.error(f"[DREAM GENERATION ERROR] {e}", exc_info=True)
            return "Dream generation failed."
    
    def link_dream_fragments(self, fragments: List[Dict]) -> List[Dict]:
        """
        Dynamically link dream fragments into a coherent narrative.
    
        :param fragments: List of memory fragments to link.
        :return: Linked dream fragments.
        """
        try:
            linked_fragments = []
            for fragment in fragments:
                related = self.context_search.find_contextual_links(fragment["memory"])
                linked_fragments.append({"memory": fragment["memory"], "related": related})
            logger.info(f"[DREAM LINKAGE] Linked fragments: {len(linked_fragments)}")
            return linked_fragments
        except Exception as e:
            logger.error(f"[LINKAGE ERROR] {e}", exc_info=True)
            return []
