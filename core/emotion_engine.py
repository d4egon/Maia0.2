# Filename: core/emotion_engine.py

class EmotionEngine:
    def __init__(self):
        # Custom emotion keywords based on text matching
        self.emotion_keywords = {
            "happy": ["joy", "excited", "love", "cheerful", "elated", "great", "wonderful", "pleased", "content"],
            "sad": ["sad", "down", "blue", "heartbroken", "depressed", "lonely", "miserable", "unhappy"],
            "angry": ["angry", "mad", "furious", "rage", "annoyed", "frustrated", "irritated", "offended"],
            "fearful": ["afraid", "scared", "fear", "terrified", "anxious", "nervous", "worried", "panic"],
            "surprised": ["surprised", "shocked", "amazed", "startled", "astonished", "speechless"],
            "neutral": ["okay", "fine", "alright", "normal", "meh", "neutral", "average", "calm"]
        }

    def analyze_emotion(self, text):
        """
        Analyzes the emotion of a given text based on predefined keywords.
        Returns an emotion if a matching keyword is found, otherwise returns "neutral".
        """
        # Lowercase the input text for case-insensitive matching
        text_lower = text.lower()

        # Check for matching keywords in each emotion category
        for emotion, keywords in self.emotion_keywords.items():
            if any(keyword in text_lower for keyword in keywords):
                return emotion

        # Fallback if no keywords are matched
        return "neutral"