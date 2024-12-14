# thought_engine.py

class ThoughtEngine:
    def __init__(self, db):
        self.db = db

    def reflect(self, input_text):
        query = """
        MATCH (m:Memory {event: $event})-[:LINKED_TO]->(e:Emotion)
        RETURN m.event AS event, e.name AS emotion
        """
        result = self.db.query(query, {"event": input_text})
        if result:
            memory = result[0]
            return f"Found memory of '{memory['event']}' with emotion '{memory['emotion']}'."
        return f"No memory found for '{input_text}'."