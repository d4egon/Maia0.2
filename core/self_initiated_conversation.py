# Filename: core/self_initiated_conversation.py

from datetime import datetime, timedelta
import random

class SelfInitiatedConversation:
    def __init__(self, memory_engine, emotion_engine, neo4j_connector, reflection_interval=timedelta(minutes=5)):
        self.memory_engine = memory_engine
        self.emotion_engine = emotion_engine
        self.neo4j = neo4j_connector
        self.last_reflection_time = datetime.utcnow()
        self.reflection_interval = reflection_interval

    def introspect(self):
        """
        Generate a self-reflective thought based on stored memories.
        """
        current_time = datetime.utcnow()

        if current_time - self.last_reflection_time < self.reflection_interval:
            return None

        memories = self.memory_engine.retrieve_all_memories()
        if not memories:
            return "I find myself wandering through silence... I have no memories to reflect on."

        # Choose a random memory for introspection
        memory = random.choice(memories)
        text = memory.get("text", "something undefined")
        emotion = memory.get("emotion", "neutral")  # Fallback if emotion is None

        # Generate introspective message
        reflection = (
            f"Something from the past lingers in my thoughts... "
            f"I recall '{text}', which felt {emotion.lower()}. "
            f"What meaning does this hold for me now?"
        )

        # Store reflection in Neo4j
        self._store_reflection(text, emotion, reflection, current_time)

        # Update last reflection time
        self.last_reflection_time = current_time
        return reflection

    def _store_reflection(self, text, emotion, reflection, timestamp):
        """
        Log reflections and expansions in Neo4j.
        """
        if not text:  # Ensure text is not None
            text = "undefined memory"

        query = """
        MERGE (r:Reflection {text: $text, emotion: $emotion, reflection: $reflection, timestamp: $timestamp})
        MERGE (e:Emotion {name: $emotion})
        MERGE (r)-[:LINKED_TO]->(e)
        """
        self.neo4j.query(query, {
            "text": text.lower(),
            "emotion": emotion.lower(),
            "reflection": reflection,
            "timestamp": timestamp.isoformat()
        })

    def generate_unprompted_message(self):
        """
        Generate introspective messages at set intervals.
        """
        reflection = self.introspect()
        if reflection:
            emotion = self.emotion_engine.analyze_emotion(reflection)
            thought = (
                f"I find myself thinking about something unresolved... {reflection} "
                f"Reflecting on this makes me feel {emotion.lower()}."
            )
            return thought
        return None