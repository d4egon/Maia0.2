class ContextualIntentDetector:
    def __init__(self, neo4j_connector):
        self.neo4j_connector = neo4j_connector

    def detect_intent(self, text):
        keywords = {
            "greeting": ["hello", "hi", "hey", "good morning", "morning", "good evening"],
            "negation": ["i don't", "i disagree", "not really", "never mind", "i refuse"],
            "confirmation": ["yes", "correct", "right", "of course", "sure", "yeah"],
            "emotion": ["happy", "sad", "angry", "excited", "bored", "calm"]
        }

        text_lower = text.lower().strip()

        # Scoring system for intents
        intent_scores = {intent: 0 for intent in keywords}

        # Check for keyword matches
        for intent, words in keywords.items():
            for word in words:
                if word in text_lower:
                    intent_scores[intent] += 1

        # Find the best match or fallback to unknown
        best_intent = max(intent_scores, key=intent_scores.get)

        if intent_scores[best_intent] == 0:
            return "unknown"

        # Avoid misclassifying short phrases as negation
        if best_intent == "negation" and len(text_lower.split()) < 3:
            return "unknown"

        return best_intent