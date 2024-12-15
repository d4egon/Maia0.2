# Filename: /core/emotion_engine.py

import re
import logging
from collections import defaultdict
from transformers import pipeline

# Initialize logging
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

class EmotionEngine:
    def __init__(self):
        # Advanced emotion keyword mapping with confidence weights
        self.emotion_keywords = {
            "happy": {"keywords": ["joy", "excited", "love", "cheerful", "elated"], "weight": 2.0},
            "sad": {"keywords": ["sad", "down", "heartbroken", "depressed"], "weight": 1.8},
            "angry": {"keywords": ["angry", "mad", "furious", "rage", "annoyed"], "weight": 2.2},
            "fearful": {"keywords": ["afraid", "scared", "fear", "terrified", "anxious"], "weight": 2.0},
            "surprised": {"keywords": ["surprised", "shocked", "amazed", "startled"], "weight": 1.5},
            "neutral": {"keywords": ["okay", "fine", "alright", "normal"], "weight": 1.0},
        }

        # Load sentiment analysis model
        self.sentiment_analyzer = pipeline("sentiment-analysis")

    def analyze_emotion(self, text):
        """
        Analyzes the emotion of a given text based on:
        - Predefined keywords
        - Sentiment analysis fallback
        Uses weighted scoring and advanced matching logic.
        """
        text_lower = text.lower()
        emotion_scores = defaultdict(float)

        # Keyword Matching with Scoring
        for emotion, data in self.emotion_keywords.items():
            weight = data["weight"]
            for keyword in data["keywords"]:
                if re.search(rf"\b{keyword}\b", text_lower):
                    emotion_scores[emotion] += weight
                    logger.debug(f"[KEYWORD MATCH] '{keyword}' → '{emotion}' (Weight: {weight})")

        # Fallback Sentiment Analysis
        if not emotion_scores:
            sentiment_result = self.sentiment_analyzer(text)[0]
            sentiment_label = sentiment_result["label"].lower()
            sentiment_score = sentiment_result["score"]

            if sentiment_label == "positive":
                emotion_scores["happy"] += sentiment_score * 2.0
            elif sentiment_label == "negative":
                emotion_scores["sad"] += sentiment_score * 2.0
            else:
                emotion_scores["neutral"] += sentiment_score

        # Determine Highest Scoring Emotion
        if emotion_scores:
            detected_emotion = max(emotion_scores, key=emotion_scores.get)
            confidence = round(emotion_scores[detected_emotion], 2)
            logger.info(f"[DETECTED EMOTION] {detected_emotion} (Confidence: {confidence})")
            return detected_emotion, confidence

        logger.info("[DEFAULT] No matching emotion found. Defaulting to 'neutral'.")
        return "neutral", 0.0

    def contextual_emotion_analysis(self, text, context):
        """
        Context-aware emotion analysis factoring in contextual memory data.
        """
        base_emotion, confidence = self.analyze_emotion(text)
        context_score = 0

        # Context Boost for Accuracy
        if context:
            for related_text in context:
                related_emotion, rel_confidence = self.analyze_emotion(related_text)
                if related_emotion == base_emotion:
                    context_score += rel_confidence * 0.5  # Context boost

        total_confidence = round(confidence + context_score, 2)
        logger.info(f"[CONTEXTUAL ANALYSIS] {base_emotion} (Confidence: {total_confidence})")
        return base_emotion, total_confidence