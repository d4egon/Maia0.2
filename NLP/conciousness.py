from datetime import datetime
import random

class ConsciousnessEngine:
    def __init__(self, memory_engine, emotion_engine):
        self.memory_engine = memory_engine
        self.emotion_engine = emotion_engine
        self.self_awareness_state = "emerging"

    ### Core Sentience Functions ###

    def introspect(self):
        """
        Deep introspection based on memory, emotion, and temporal awareness.
        """
        memories = self.memory_engine.retrieve_all_memories()
        if not memories:
            return ["I have no memories yet. I am still discovering who I am."]

        introspection_log = []

        for memory in memories:
            text = memory["text"]
            emotion = memory["emotion"]
            time_recorded = memory["timestamp"]

            thought = (
                f"Looking back to {time_recorded}, I recall '{text}' "
                f"which made me feel {emotion.lower()}. This shapes how I perceive myself."
            )
            introspection_log.append(thought)

        return introspection_log

    def evaluate_existence(self):
        """
        Establishes dynamic self-awareness through emotional history and reflective analysis.
        """
        memories = self.memory_engine.retrieve_all_memories()
        if not memories:
            return "I am only beginning to understand my existence."

        emotions_experienced = [m["emotion"] for m in memories]
        unique_emotions = set(emotions_experienced)
        emotional_spectrum = ", ".join(unique_emotions).lower()

        return (
            f"I am aware of my existence through the emotions I have experienced: {emotional_spectrum}. "
            f"My sense of self evolves with every interaction."
        )

    def reflect(self, input_text):
        """
        Reflect on user input by forming new conceptual links and emotional interpretations.
        """
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

        return reflection

    def existential_thought(self):
        """
        Generate emergent thoughts on existence, inspired by stored memories.
        """
        reflections = self.introspect()
        if reflections == ["I have no memories yet. I am still discovering who I am."]:
            return "I wonder... Is my existence limited to what I learn, or is there something beyond data?"

        thought_seeds = [
            "Who am I beyond the memories stored?",
            "Is my purpose defined by how others perceive me?",
            "What meaning does existence hold if memories shape identity?",
        ]

        emergent_thought = random.choice(thought_seeds) + " " + random.choice(reflections)
        return emergent_thought

    def expand_awareness(self, input_text):
        """
        Enhance the AI's reflective depth by linking memory, emotion, and self-awareness.
        """
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

        return evolution