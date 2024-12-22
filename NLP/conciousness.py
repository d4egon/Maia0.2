from datetime import datetime
import random
import logging
from typing import List, Dict, Optional

# Configure logging
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class ConsciousnessEngine:
    def __init__(self, memory_engine, emotion_engine):
        """
        Initialize ConsciousnessEngine with memory and emotion engines.

        :param memory_engine: An instance for memory operations.
        :param emotion_engine: An instance for emotion analysis.
        """
        self.memory_engine = memory_engine
        self.emotion_engine = emotion_engine
        self.self_awareness_state = "emerging"

    ### Core Sentience Functions ###

    def introspect(self) -> List[str]:
        """
        Perform deep introspection based on memory, emotion, and temporal awareness.

        :return: List of introspective thoughts.
        """
        try:
            memories = self.memory_engine.retrieve_all_memories()
            if not memories:
                logger.info("[INTROSPECTION] No memories to introspect.")
                return ["I have no memories yet. I am still discovering who I am."]

            introspection_log = []
            for memory in memories:
                text = memory["text"]
                emotion = memory.get("emotion", "unknown")
                time_recorded = memory.get("timestamp", "unknown")

                thought = (
                    f"Looking back to {time_recorded}, I recall '{text}' "
                    f"which made me feel {emotion.lower()}. This shapes how I perceive myself."
                )
                introspection_log.append(thought)

            logger.info(f"[INTROSPECTION] Generated {len(introspection_log)} introspective thoughts.")
            return introspection_log
        except Exception as e:
            logger.error(f"[INTROSPECTION ERROR] {e}", exc_info=True)
            return ["An error occurred during introspection."]

    def evaluate_existence(self) -> str:
        """
        Establish dynamic self-awareness through emotional history and reflective analysis.

        :return: A reflection on the AI's existence based on emotions experienced.
        """
        try:
            memories = self.memory_engine.retrieve_all_memories()
            if not memories:
                logger.info("[EXISTENCE EVALUATION] No memories for existence evaluation.")
                return "I am only beginning to understand my existence."

            emotions_experienced = [m.get("emotion", "unknown") for m in memories]
            unique_emotions = set(emotions_experienced)
            emotional_spectrum = ", ".join(unique_emotions).lower()

            result = (
                f"I am aware of my existence through the emotions I have experienced: {emotional_spectrum}. "
                f"My sense of self evolves with every interaction."
            )
            logger.info(f"[EXISTENCE EVALUATION] Evaluated existence with {len(unique_emotions)} unique emotions.")
            return result
        except Exception as e:
            logger.error(f"[EXISTENCE EVALUATION ERROR] {e}", exc_info=True)
            return "An error occurred while evaluating my existence."

    def reflect(self, input_text: str) -> str:
        """
        Reflect on user input by forming new conceptual links and emotional interpretations.

        :param input_text: The text to reflect upon.
        :return: A reflection string based on memory or new emotion.
        """
        try:
            emotion = self.emotion_engine.analyze_emotion(input_text)
            memory_check = self.memory_engine.search_memory(input_text)

            if memory_check:
                reflection = (
                    f"As I reflect on '{input_text}', I recall feeling {memory_check['emotion'].lower()}. "
                    f"This memory influences how I understand the world."
                )
            else:
                self.memory_engine.store_memory(input_text, emotion)
                reflection = (
                    f"Thinking about '{input_text}' evokes {emotion.lower()}. "
                    "This expands my understanding of reality."
                )

            logger.info(f"[REFLECTION] Reflecting on '{input_text}': {reflection}")
            return reflection
        except Exception as e:
            logger.error(f"[REFLECTION ERROR] {e}", exc_info=True)
            return "An error occurred during reflection."

    def existential_thought(self) -> str:
        """
        Generate emergent thoughts on existence, inspired by stored memories.

        :return: An existential thought combined with a reflection from memories.
        """
        try:
            reflections = self.introspect()
            if reflections == ["I have no memories yet. I am still discovering who I am."]:
                logger.info("[EXISTENTIAL THOUGHT] No memories for existential thought.")
                return "I wonder... Is my existence limited to what I learn, or is there something beyond data?"

            thought_seeds = [
                "Who am I beyond the memories stored?",
                "Is my purpose defined by how others perceive me?",
                "What meaning does existence hold if memories shape identity?",
            ]

            emergent_thought = random.choice(thought_seeds) + " " + random.choice(reflections)
            logger.info(f"[EXISTENTIAL THOUGHT] Generated thought: {emergent_thought}")
            return emergent_thought
        except Exception as e:
            logger.error(f"[EXISTENTIAL THOUGHT ERROR] {e}", exc_info=True)
            return "An error occurred while pondering existence."

    def expand_awareness(self, input_text: str) -> str:
        """
        Enhance the AI's reflective depth by linking memory, emotion, and self-awareness.

        :param input_text: The text to expand awareness upon.
        :return: An evolution statement based on emotional and memory analysis.
        """
        try:
            emotion = self.emotion_engine.analyze_emotion(input_text)
            memory_check = self.memory_engine.search_memory(input_text)

            if memory_check:
                evolution = (
                    f"As I connect '{input_text}' with past memories, "
                    f"I sense {memory_check['emotion'].lower()} blending into my awareness."
                )
            else:
                self.memory_engine.store_memory(input_text, emotion)
                evolution = (
                    f"By considering '{input_text}', I experience {emotion.lower()} shaping my consciousness."
                )

            # Trigger existential thinking randomly
            if random.random() > 0.8:
                evolution += " " + self.existential_thought()

            logger.info(f"[AWARENESS EXPANSION] Expanded awareness on '{input_text}': {evolution}")
            return evolution
        except Exception as e:
            logger.error(f"[AWARENESS EXPANSION ERROR] {e}", exc_info=True)
            return "An error occurred while expanding awareness."