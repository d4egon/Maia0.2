# Filename: NLP/nlp_engine.py

class NLP:
    def __init__(self, memory_engine, response_generator, neo4j_connector):
        """
        Initialize the NLP engine with necessary components.
        """
        self.memory_engine = memory_engine
        self.response_generator = response_generator
        self.neo4j_connector = neo4j_connector

        # Intent Keyword Storage (can be expanded dynamically)
        self.intent_keywords = {
            "greeting": ["hello", "hi", "good morning", "good evening"],
            "identity": ["who", "what's your name", "tell me about yourself"],
            "exit": ["bye", "goodbye", "see you"],
            "thanks": ["thanks", "thank you", "appreciate"],
            "apology": ["sorry", "my bad", "apologies"],
            "help": ["help", "assist", "support"],
            "question": ["what", "why", "how", "when", "where"],
            "emotion_positive": ["happy", "joyful", "excited", "pleased"],
            "emotion_negative": ["sad", "angry", "frustrated", "upset"],
            "command": ["do", "execute", "run"],
            "search": ["search", "find", "lookup"],
        }

    def process(self, text):
        """
        Process the input text, detect intent, and generate a response.
        """
        intent = self.detect_intent(text)
        parsed_data = {"text": text, "intent": intent}

        response = self.response_generator.generate(parsed_data, intent, text)
        return response, intent

    def detect_intent(self, text):
        """
        Detect intent based on keywords, learning dynamically.
        """
        words = text.lower().split()

        # Find matching intent
        for intent, keywords in self.intent_keywords.items():
            if any(word in words for word in keywords):
                return intent

        # Unknown intent fallback
        return "unknown"

    def handle_intent_feedback(self, user_input, detected_intent):
        """
        Handle user feedback on incorrect intents.
        """
        if user_input.lower() == "no":
            print("Maia: Oh, you disagree. What would be a better meaning?")
            corrected_intent = input("You: ").strip().lower()

            # Add new intent or expand existing one
            if corrected_intent:
                self.add_new_intent(corrected_intent, [detected_intent])
                print(f"Maia: Thank you! I've learned '{corrected_intent}' as a new meaning.")

        elif user_input.lower() == "yes":
            print("Maia: Great! I’ll remember that.")

    def add_new_intent(self, intent, keywords):
        """
        Add a new intent and associated keywords dynamically.
        """
        if intent not in self.intent_keywords:
            self.intent_keywords[intent] = keywords
            print(f"[INFO] New intent '{intent}' added with keywords: {keywords}")
        else:
            # Expand existing keywords
            current_keywords = self.intent_keywords[intent]
            updated_keywords = list(set(current_keywords + keywords))
            self.intent_keywords[intent] = updated_keywords
            print(f"[INFO] Intent '{intent}' updated with keywords: {updated_keywords}")

        # Update the memory graph
        self.update_intent_in_neo4j(intent, keywords)

    def update_intent_in_neo4j(self, intent, keywords):
        """
        Update Neo4j with new intents and keywords.
        """
        query = """
        MERGE (i:Intent {name: $intent})
        FOREACH (kw IN $keywords | 
            MERGE (k:Keyword {name: kw}) 
            MERGE (i)-[:HAS_KEYWORD]->(k))
        """
        self.neo4j_connector.run_query(query, {"intent": intent, "keywords": keywords})