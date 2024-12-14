class IntentDetector:
    def __init__(self):
        self.intents = {
            "greeting": ["hello", "hi", "hey", "greetings", "good morning", "good evening", "howdy", "salutations"],
            "identity": ["who", "what", "name", "you", "your purpose", "identity", "self", "origin"],
            "exit": ["bye", "exit", "quit", "goodbye", "see you later", "farewell", "adios", "later"],
            "question": ["what", "why", "how", "when", "where", "which", "could", "do"],
            "confirmation": ["yes", "yeah", "sure", "okay", "indeed", "affirmative", "right", "correct"],
            "negation": ["no", "nope", "not", "never", "negative", "disagree", "wrong", "nah"],
            "thanks": ["thank", "thanks", "appreciate", "grateful", "appreciation", "thanks a lot", "cheers"],
            "apology": ["sorry", "apologize", "excuse", "pardon", "regret", "my bad", "oops"],
            "request": ["can", "could", "would", "please", "may", "want", "need", "wish"],
            "order": ["buy", "order", "purchase", "get", "need", "require", "acquire", "fetch"],
            "location": ["address", "location", "place", "where", "directions", "map", "GPS"],
            "time": ["time", "when", "duration", "schedule", "appointment", "clock", "timer"],
            "weather": ["weather", "temperature", "forecast", "climate", "rain", "snow", "sunny"],
            "calculation": ["calculate", "compute", "math", "add", "subtract", "multiply", "divide", "average"],
            "search": ["search", "find", "look", "google", "research", "investigate", "browse", "explore"],
            "information": ["info", "details", "data", "facts", "knowledge", "learn", "educate", "enlighten"],
            "help": ["help", "support", "assistance", "guide", "advice", "tutorial", "mentor", "coach"],
            "contact": ["contact", "email", "phone", "call", "reach", "connect", "message", "text"],
            "reminder": ["remind", "reminder", "alert", "notify", "note", "memo", "alarm", "cue"],
            "entertainment": ["movie", "music", "book", "game", "play", "watch", "listen", "read"],
            "complaint": ["complain", "issue", "problem", "dispute", "unhappy", "annoyed", "frustrated", "dissatisfied"],
            "feedback": ["feedback", "opinion", "review", "comment", "suggest", "rate", "critique", "evaluate"],
            "translation": ["translate", "language", "interpret", "conversion", "phrase", "word", "lingo", "dialect"],
            "health": ["health", "symptom", "doctor", "medicine", "illness", "fitness", "wellness", "diagnose"],
            "travel": ["travel", "trip", "vacation", "journey", "flight", "destination", "tour", "adventure"],
            "food": ["food", "recipe", "cook", "eat", "restaurant", "meal", "dine", "cuisine"],
            "technology": ["tech", "device", "software", "app", "gadget", "code", "program", "hack"],
            "news": ["news", "current", "event", "update", "headline", "article", "report", "breaking"],
            "sports": ["sport", "game", "score", "team", "athlete", "match", "championship", "tournament"],
            "education": ["learn", "study", "school", "education", "course", "teach", "tutor", "lecture"],
            "finance": ["money", "finance", "bank", "invest", "stock", "price", "budget", "savings"],
            "social": ["friend", "chat", "meet", "date", "party", "socialize", "network", "connect"],
            "fun": ["fun", "enjoy", "laugh", "celebrate", "party", "joke", "amuse", "entertain"],
            "philosophy": ["think", "philosophy", "life", "meaning", "truth", "exist", "ponder", "reflect"],
            "sci-fi": ["sci-fi", "science fiction", "space", "aliens", "future", "technology", "dystopia", "utopia"],
            "history": ["history", "past", "event", "era", "ancient", "medieval", "historical", "legacy"],
            "art": ["art", "painting", "sculpture", "music", "dance", "theater", "cinema", "literature"],
            "politics": ["politics", "government", "election", "policy", "law", "vote", "democracy", "diplomacy"],
            "environment": ["environment", "nature", "climate", "ecology", "conservation", "green", "sustain", "pollution"],
            "pets": ["pet", "dog", "cat", "animal", "care", "vet", "groom", "adopt"],
            "fashion": ["fashion", "style", "clothing", "wear", "trend", "design", "outfit", "look"],
            "psychology": ["psychology", "mind", "behavior", "emotion", "therapy", "mental", "counsel", "personality"],
        }

    def detect_intent(self, tokens):
        for intent, keywords in self.intents.items():
            if any(token.lower() in keywords for token in tokens):
                return intent
        return "unknown"