# Filename: /core/emotion_fusion_engine.py

import logging
from typing import Dict, List, Tuple
from core.emotion_engine import EmotionEngine

# Configure logging
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class EmotionFusionEngine:
    def __init__(self, memory_engine, nlp_engine):
        """
        Initialize the EmotionFusionEngine with memory and NLP engines.

        :param memory_engine: An instance for memory operations.
        :param nlp_engine: An instance for NLP operations.
        """
        self.emotion_engine = EmotionEngine()
        self.memory_engine = memory_engine
        self.nlp_engine = nlp_engine

    def fuse_emotions(self, visual_input: str, text_input: str) -> str:
        """
        Fuse emotions from visual analysis, text context, and memory search results.

        :param visual_input: Description or path of visual input.
        :param text_input: Textual input to analyze.
        :return: The final determined emotion.
        """
        logger.info("[FUSION] Starting emotion fusion process.")

        try:
            # Analyze emotions separately
            visual_emotion, visual_confidence = self.analyze_visual_emotion(visual_input)
            text_emotion, text_confidence = self.analyze_text_emotion(text_input)

            # Search contextual memory
            context_data = self.memory_engine.search_memory(text_input)
            context_emotion, context_confidence = self.analyze_context_emotion(context_data)

            # Decision Fusion Logic
            final_emotion = self.determine_final_emotion(
                visual_emotion, visual_confidence,
                text_emotion, text_confidence,
                context_emotion, context_confidence
            )

            # Store the fused memory
            self.memory_engine.store_memory(
                f"Image emotion: {visual_emotion}, NLP emotion: {text_emotion}, Context emotion: {context_emotion}",
                final_emotion,
                additional_data={"visual_input": visual_input, "text_input": text_input}
            )

            logger.info(f"[FUSION RESULT] Final Emotion: {final_emotion}")
            return final_emotion
        except Exception as e:
            logger.error(f"[FUSION ERROR] {e}", exc_info=True)
            return "neutral"  # Default to neutral if fusion fails

    def analyze_visual_emotion(self, visual_input: str) -> Tuple[str, float]:
        """
        Placeholder for analyzing emotions from visual data (image-based).

        :param visual_input: Visual input to analyze.
        :return: Tuple of (emotion, confidence).
        """
        try:
            logger.info("[VISUAL] No visual emotion model implemented yet.")
            return "neutral", 0.0
        except Exception as e:
            logger.error(f"[VISUAL FAILED] {e}")
            return "neutral", 0.0

    def analyze_text_emotion(self, text_input: str) -> Tuple[str, float]:
        """
        Analyze emotions from text data using the Emotion Engine.

        :param text_input: Text to analyze for emotion.
        :return: Tuple of (emotion, confidence).
        """
        try:
            text_emotion, confidence = self.emotion_engine.analyze_emotion(text_input)
            logger.info(f"[TEXT] Detected Emotion: {text_emotion} (Confidence: {confidence})")
            return text_emotion, confidence
        except Exception as e:
            logger.error(f"[TEXT FAILED] {e}")
            return "neutral", 0.0

    def analyze_context_emotion(self, context_data: List[Dict]) -> Tuple[str, float]:
        """
        Analyze emotions from context-related memory search results.

        :param context_data: List of memory contexts to analyze.
        :return: Tuple of (emotion, confidence).
        """
        try:
            if not context_data:
                logger.info("[CONTEXT] No relevant context found.")
                return "neutral", 0.0

            context_text = " ".join([m["text"] for m in context_data])
            context_emotion, confidence = self.emotion_engine.contextual_emotion_analysis(
                text=context_text,
                context=[m["text"] for m in context_data]
            )
            logger.info(f"[CONTEXT] Detected Emotion: {context_emotion} (Confidence: {confidence})")
            return context_emotion, confidence
        except Exception as e:
            logger.error(f"[CONTEXT FAILED] {e}")
            return "neutral", 0.0

    def determine_final_emotion(
        self,
        visual_emotion: str, visual_confidence: float,
        text_emotion: str, text_confidence: float,
        context_emotion: str, context_confidence: float
    ) -> str:
        """
        Determine the final emotion based on the highest cumulative confidence score.

        :param visual_emotion: Emotion from visual analysis.
        :param visual_confidence: Confidence score for visual emotion.
        :param text_emotion: Emotion from text analysis.
        :param text_confidence: Confidence score for text emotion.
        :param context_emotion: Emotion from context analysis.
        :param context_confidence: Confidence score for context emotion.
        :return: The emotion with the highest cumulative confidence.
        """
        emotions = {
            visual_emotion: visual_confidence,
            text_emotion: text_confidence,
            context_emotion: context_confidence
        }

        final_emotion = max(emotions, key=emotions.get)
        total_confidence = round(emotions[final_emotion], 2)
        logger.info(f"[FINAL EMOTION] {final_emotion} (Total Confidence: {total_confidence})")
        return final_emotion