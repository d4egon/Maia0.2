class MemoryEngine:
    def __init__(self, db):
        self.db = db

    def store_memory(self, text, emotion):
        query = """
        MERGE (m:Memory {text: $text})
        SET m.emotion = $emotion
        """
        self.db.run_query(query, {"text": text.lower(), "emotion": emotion.lower()})

    def search_memory(self, text):
        query = """
        MATCH (m:Memory {text: $text}) 
        RETURN m.emotion, m.weight
        """
        result = self.db.run_query(query, {"text": text.lower()})
        return result[0] if result else None

    def apply_memory_decay(self, decay_factor=0.1):
        query = """
        MATCH (m:Memory)
        WHERE m.weight > 0
        SET m.weight = m.weight - $decay_factor
        """
        self.db.run_query(query, {"decay_factor": decay_factor})

    def adjust_memory_weight(self, text, adjustment):
        query = """
        MATCH (m:Memory {text: $text})
        SET m.weight = COALESCE(m.weight, 0) + $adjustment
        """
        self.db.run_query(query, {"text": text.lower(), "adjustment": adjustment})