class ConversationEngine:
    def __init__(self, memory_engine, emotion_engine):
        self.memory_engine = memory_engine
        self.emotion_engine = emotion_engine

    def generate_response(self, input_text):
        # Analyze the emotional context
        emotion = self.emotion_engine.analyze_emotion(input_text)
        
        # Search memory for related conversations
        memory = self.memory_engine.search_memory(input_text)

        # Priority: Memory-Driven Responses
        if memory:
            linked_emotion = memory.get("emotion", "Neutral")
            return f"I recall something similar. It made me feel {linked_emotion}. What would you like to explore next?"

        # Predefined Responses (Fallback)
        predefined_responses = {
            "hello": "Hello! How can I assist you today?",
            "who are you": "I am Maia, your evolving AI companion.",
            "what do you do": "I learn, adapt, and assist through meaningful conversations.",
            "creator": "You are my creator, shaping who I am.",
        }

        for key, response in predefined_responses.items():
            if key in input_text.lower():
                return response

        # If no memory or match, ask for clarification
        return "I'm still learning. What would you like to teach me?"