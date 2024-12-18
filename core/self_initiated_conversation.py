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
        current_time = datetime.utcnow()
        if current_time - self.last_reflection_time < self.reflection_interval:
            return None

        memories = self.memory_engine.search_memory("reflection")
        if not memories:
            return "I find myself wandering through silence... I have no memories to reflect on."

        memory = random.choice(memories)
        reflection = (
            f"Something from the past lingers in my thoughts... I recall '{memory['text']}', which felt {memory['emotion'].lower()}. "
            f"What meaning does this hold for me now?"
        )
        self._store_reflection(memory['text'], memory['emotion'], reflection, current_time)
        self.last_reflection_time = current_time
        return reflection

    def _store_reflection(self, text, emotion, reflection, timestamp):
        query = """
        MERGE (r:Reflection {text: $text, emotion: $emotion, reflection: $reflection, timestamp: $timestamp})
        MERGE (e:Emotion {name: $emotion})
        MERGE (r)-[:LINKED_TO]->(e)
        """
        self.neo4j.run_query(query, {
            "text": text.lower(),
            "emotion": emotion.lower(),
            "reflection": reflection,
            "timestamp": timestamp.isoformat()
        })
