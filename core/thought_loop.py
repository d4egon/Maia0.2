#/core/thought_loop.py

import logging
import random
import time
from typing import List, Dict, Optional
from core.memory_engine import MemoryEngine
from core.conversation_engine import ConversationEngine

# Configure logging
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Thought Loop Module
class ThoughtLoop:
    def __init__(self, memory_engine: MemoryEngine, thought_engine):
        self.memory_engine = memory_engine
        self.thought_engine = thought_engine
        self.running = False

    def run(self):
        """
        Continuously run uninitiated thought loops.
        """
        self.running = True
        logger.info("[THOUGHT LOOP] Starting autonomous thought loops.")
        while self.running:
            try:
                # Generate a thought
                thought = self.thought_engine.generate_thought()
                logger.info(f"[THOUGHT LOOP] Generated Thought: {thought}")

                # Process thought for new vocabulary
                new_words = self.thought_engine.detect_new_words(thought)
                for word, meaning in new_words.items():
                    self.memory_engine.store_new_word(word, meaning)

                # Simulate interaction patterns
                self.thought_engine.learn_interaction_patterns(thought)

                # Pause before next loop iteration
                time.sleep(random.uniform(5, 15))

            except Exception as e:
                logger.error(f"[THOUGHT LOOP ERROR] {e}", exc_info=True)

    def stop(self):
        """
        Stop the thought loop.
        """
        self.running = False
        logger.info("[THOUGHT LOOP] Thought loop has been stopped.")

# Emotion Engine Module
class EmotionEngine:
    def __init__(self, memory_engine: MemoryEngine):
        self.memory_engine = memory_engine

    def tag_emotion(self, thought: str) -> str:
        """
        Determine the emotion associated with a thought.
        """
        if "happy" in thought.lower():
            return "joy"
        elif "uncertain" in thought.lower() or "?" in thought:
            return "doubt"
        elif "sad" in thought.lower():
            return "sadness"
        else:
            return "neutral"

    def process_emotion(self, thought: str):
        """
        Process and tag the emotional state of a thought.
        """
        emotion = self.tag_emotion(thought)
        self.memory_engine.tag_memory(thought, emotion)
        logger.info(f"[EMOTION ENGINE] Tagged '{thought}' with emotion: {emotion}")
        return emotion

    def concurrent_thought_processing(self, thoughts: List[str]):
        """
        Process multiple thoughts concurrently.
    
        :param thoughts: List of thoughts to process.
        """
        from concurrent.futures import ThreadPoolExecutor
        try:
            with ThreadPoolExecutor() as executor:
                results = executor.map(self.thought_engine.reflect, thoughts)
                for result in results:
                    logger.info(f"[CONCURRENT PROCESSING] {result}")
        except Exception as e:
            logger.error(f"[CONCURRENT ERROR] {e}")
