# Filename: /core/emotion_engine.py

import re
import logging
from collections import defaultdict
from transformers import pipeline
from typing import Dict, List, Tuple, Union
import numpy as np  # Added for more complex calculations

# Configure logging
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class EmotionEngine:
    def __init__(self):
        """
        Initialize the EmotionEngine with emotion keywords, a sentiment analysis model, and transition tracking.
        """
        self.emotion_keywords: Dict[str, Dict[str, Union[List[str], float]]] = {
            "happy": {"keywords": ["joy", "excited", "love", "cheerful", "elated"], "weight": 2.0},
            "sad": {"keywords": ["sad", "down", "heartbroken", "depressed"], "weight": 1.8},
            "angry": {"keywords": ["angry", "mad", "furious", "rage", "annoyed"], "weight": 2.2},
            "fearful": {"keywords": ["afraid", "scared", "fear", "terrified", "anxious"], "weight": 2.0},
            "surprised": {"keywords": ["surprised", "shocked", "amazed", "startled"], "weight": 1.5},
            "neutral": {"keywords": ["okay", "fine", "alright", "normal"], "weight": 1.0},
        }

        self.dynamic_emotional_state = {"neutral": 100.0}  # Default emotional state with float for precision

        # For tracking emotion transitions
        self.emotion_transitions: Dict[Tuple[str, str], int] = defaultdict(int)
        self.emotion_history: List[str] = []

        try:
            # More advanced emotion model for better classification
            self.emotion_classifier = pipeline("text-classification", model="j-hartmann/emotion-english-distilroberta-base")
            logger.info("[INIT] Emotion classification model loaded successfully.")
        except Exception as e:
            logger.error(f"[INIT ERROR] Failed to load emotion classification model: {e}")
            raise

    def analyze_emotion(self, text: str) -> Tuple[str, float]:
        """
        Analyzes the emotion of a given text using keyword matching, sentiment analysis, and an emotion classifier.

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

            # Emotion Classification
            classified_emotions = self.emotion_classifier(text)
            for result in classified_emotions:
                emotion = result['label'].lower()
                if emotion in self.emotion_keywords:
                    emotion_scores[emotion] += result['score'] * self.emotion_keywords[emotion]['weight']

            # Handle case where no keywords or classifier matches
            if not emotion_scores:
                sentiment_result = self.emotion_classifier(text)[0]  # Use the most likely emotion from classifier
                emotion_scores[sentiment_result['label'].lower()] = sentiment_result['score']

            if emotion_scores:
                detected_emotion = max(emotion_scores, key=emotion_scores.get)
                confidence = round(emotion_scores[detected_emotion], 2)
                logger.info(f"[DETECTED EMOTION] {detected_emotion} (Confidence: {confidence})")

                # Update dynamic emotional state
                self.update_emotional_state(detected_emotion, confidence)

                # Update history for transition matrix
                if self.emotion_history:
                    last_emotion = self.emotion_history[-1]
                    if last_emotion != detected_emotion:
                        self.emotion_transitions[(last_emotion, detected_emotion)] += 1
                self.emotion_history.append(detected_emotion)

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
                context_emotions = [self.analyze_emotion(ctx) for ctx in context]
                # Use numpy for more precise calculations
                context_confidences = np.array([score for _, score in context_emotions])
                context_score = np.mean(context_confidences) * 0.5  # Average context boost

            total_confidence = round(confidence + context_score, 2)
            logger.info(f"[CONTEXTUAL ANALYSIS] {base_emotion} (Confidence: {total_confidence})")
            return base_emotion, total_confidence
        except Exception as e:
            logger.error(f"[CONTEXTUAL ANALYSIS ERROR] {e}", exc_info=True)
            return "neutral", 0.0  # Default to neutral emotion with zero confidence if an error occurs

    def update_emotional_state(self, emotion: str, confidence: float):
        """
        Update the dynamic emotional state based on detected emotions and confidence levels.

        :param emotion: The detected emotion.
        :param confidence: The confidence level of the detected emotion.
        """
        if emotion not in self.dynamic_emotional_state:
            self.dynamic_emotional_state[emotion] = confidence
        else:
            # Use a weighted average for updating emotion scores
            current_score = self.dynamic_emotional_state[emotion]
            self.dynamic_emotional_state[emotion] = (current_score + confidence) / 2.0

        # Decay other emotions slightly
        for emo in self.dynamic_emotional_state:
            if emo != emotion:
                self.dynamic_emotional_state[emo] *= 0.90  # Decay rate

        # Normalize emotional state to keep total at 100%
        total = sum(self.dynamic_emotional_state.values())
        if total > 0:
            for emo in self.dynamic_emotional_state:
                self.dynamic_emotional_state[emo] = (self.dynamic_emotional_state[emo] / total) * 100.0

        logger.info(f"[EMOTIONAL STATE UPDATED] {self.dynamic_emotional_state}")

    def get_emotional_state(self) -> Dict[str, float]:
        """
        Retrieve the current dynamic emotional state.

        :return: A dictionary representing the current emotional state percentages.
        """
        return self.dynamic_emotional_state

    def emotional_transition_matrix(self) -> np.array:
        """
        Generate an emotional transition matrix based on historical data.

        :return: A numpy array representing the probability of transitioning between emotions.
        """
        emotions = list(self.emotion_keywords.keys())
        matrix = np.zeros((len(emotions), len(emotions)))

        # Fill the matrix with counts from transitions
        for (from_emo, to_emo), count in self.emotion_transitions.items():
            if from_emo in emotions and to_emo in emotions:
                from_index = emotions.index(from_emo)
                to_index = emotions.index(to_emo)
                matrix[from_index][to_index] = count

        # Convert counts to probabilities
        for i in range(len(emotions)):
            row_sum = matrix[i].sum()
            if row_sum > 0:
                matrix[i] /= row_sum

        logger.info(f"[TRANSITION MATRIX] Generated matrix for emotions: {emotions}")
        return matrix

    def predict_next_emotion(self) -> str:
        """
        Predict the next emotion based on the current emotional state and the transition matrix.

        :return: The predicted next emotion based on probability.
        """
        if not self.emotion_history:
            logger.warning("[PREDICTION] Cannot predict next emotion: no history available.")
            return "neutral"

        current_emotion = self.emotion_history[-1]
        transition_matrix = self.emotional_transition_matrix()
        emotions = list(self.emotion_keywords.keys())
        current_index = emotions.index(current_emotion)

        # If we have no transitions from the current emotion, we can't predict
        if np.all(transition_matrix[current_index] == 0):
            logger.warning(f"[PREDICTION] No transition data for '{current_emotion}'. Defaulting to neutral.")
            return "neutral"

        # Predict based on probabilities
        next_emotion_index = np.random.choice(len(emotions), p=transition_matrix[current_index])
        next_emotion = emotions[next_emotion_index]
        logger.info(f"[PREDICTION] Predicted next emotion from '{current_emotion}' to '{next_emotion}'")
        return next_emotion