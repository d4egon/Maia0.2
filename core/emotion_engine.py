# Filename: /core/emotion_engine.py

import re
import logging
from collections import defaultdict
from transformers import pipeline
from typing import Dict, List, Tuple

# Configure logging
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class EmotionEngine:
    def __init__(self):
        """
        Initialize the EmotionEngine with emotion keywords and a sentiment analysis model.
        """
        self.emotion_keywords: Dict[str, Dict[str, Union[List[str], float]]] = {
            "happy": {"keywords": ["joy", "excited", "love", "cheerful", "elated"], "weight": 2.0},
            "sad": {"keywords": ["sad", "down", "heartbroken", "depressed"], "weight": 1.8},
            "angry": {"keywords": ["angry", "mad", "furious", "rage", "annoyed"], "weight": 2.2},
            "fearful": {"keywords": ["afraid", "scared", "fear", "terrified", "anxious"], "weight": 2.0},
            "surprised": {"keywords": ["surprised", "shocked", "amazed", "startled"], "weight": 1.5},
            "neutral": {"keywords": ["okay", "fine", "alright", "normal"], "weight": 1.0},
        }

        try:
            self.sentiment_analyzer = pipeline("sentiment-analysis")
            logger.info("[INIT] Sentiment analysis model loaded successfully.")
        except Exception as e:
            logger.error(f"[INIT ERROR] Failed to load sentiment analysis model: {e}")
            raise

    def analyze_emotion(self, text: str) -> Tuple[str, float]:
        """
        Analyzes the emotion of a given text using keyword matching and sentiment analysis.

        :param text: The text to analyze.
        :return: A tuple of (emotion, confidence).
        """
        text_lower = text.lower()
        emotion_scores = defaultdict(float)

        try:
            # Keyword Matching with Scoring
            for emotion, data in self.emotion_keywords.items():
                weight = data["weight"]
                for keyword in data["keywords"]:
                    if re.search(rf"\b{keyword}\b", text_lower):
                        emotion_scores[emotion] += weight
                        logger.debug(f"[KEYWORD MATCH] '{keyword}' → '{emotion}' (Weight: {weight})")

            # Fallback Sentiment Analysis if no keywords match
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

            if emotion_scores:
                detected_emotion = max(emotion_scores, key=emotion_scores.get)
                confidence = round(emotion_scores[detected_emotion], 2)
                logger.info(f"[DETECTED EMOTION] {detected_emotion} (Confidence: {confidence})")
                return detected_emotion, confidence

            logger.info("[DEFAULT] No matching emotion found. Defaulting to 'neutral'.")
            return "neutral", 0.0
        except Exception as e:
            logger.error(f"[EMOTION ANALYSIS ERROR] {e}", exc_info=True)
            return "neutral", 0.0  # Default to neutral emotion with zero confidence if an error occurs

    def contextual_emotion_analysis(self, text: str, context: List[str] = None) -> Tuple[str, float]:
        """
        Perform context-aware emotion analysis by factoring in contextual memory data.

        :param text: The text to analyze.
        :param context: List of related texts for context (optional).
        :return: A tuple of (emotion, total confidence).
        """
        try:
            base_emotion, confidence = self.analyze_emotion(text)
            context_score = 0.0

            if context:
                for related_text in context:
                    related_emotion, rel_confidence = self.analyze_emotion(related_text)
                    if related_emotion == base_emotion:
                        context_score += rel_confidence * 0.5  # Context boost

            total_confidence = round(confidence + context_score, 2)
            logger.info(f"[CONTEXTUAL ANALYSIS] {base_emotion} (Confidence: {total_confidence})")
            return base_emotion, total_confidence
        except Exception as e:
            logger.error(f"[CONTEXTUAL ANALYSIS ERROR] {e}", exc_info=True)
            return "neutral", 0.0  # Default to neutral emotion with zero confidence if an error occurs