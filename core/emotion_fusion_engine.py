# Filename: /core/emotion_fusion_engine.py

import logging
import fileinput
from core.emotion_engine import EmotionEngine

# Initialize logging
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

class EmotionFusionEngine:
    def __init__(self, memory_engine, nlp_engine):
        self.emotion_engine = EmotionEngine()
        self.memory_engine = memory_engine
        self.nlp_engine = nlp_engine

    def fuse_emotions(self, visual_input, text_input):
        """
        Fuse emotions from visual analysis, text context, and memory search results.
        """
        logger.info("[FUSION] Starting emotion fusion process.")

        # Analyze emotions separately
        visual_emotion, visual_confidence = self.analyze_visual_emotion(visual_input)
        text_emotion, text_confidence = self.analyze_text_emotion(text_input)

        # Search contextual memory
        context_data = self.memory_engine.search_memory(text_input)
        context_emotion, context_confidence = self.analyze_context_emotion(context_data)
        fused_emotion = self.emotion_fusion_engine.fuse_emotions(visual_input=None, text_input=user_input)
        response = self.response_generator.generate("query", user_input, emotion=fused_emotion)

        # Decision Fusion Logic
        final_emotion = self.determine_final_emotion(
            visual_emotion, visual_confidence,
            text_emotion, text_confidence,
            context_emotion, context_confidence
        )

        # Store the fused memory
        self.memory_engine.store_memory(
            f"Image emotion: {visual_emotion}, NLP emotion: {text_emotion}",
            final_emotion,
            additional_data={"visual_input": visual_input, "text_input": text_input}
        )

        logger.info(f"[FUSION RESULT] Final Emotion: {final_emotion}")
        return final_emotion

    def analyze_visual_emotion(self, visual_input):
        """
        Analyze emotions from visual data (image-based).
        """
        try:
            # Placeholder for future ML-based visual emotion detection
            logger.info("[VISUAL] No visual emotion model implemented yet.")
            return "neutral", 0.0
        except Exception as e:
            logger.error(f"[VISUAL FAILED] {e}")
            return "neutral", 0.0

    def analyze_text_emotion(self, text_input):
        """
        Analyze emotions from text data using the Emotion Engine.
        """
        try:
            text_emotion, confidence = self.emotion_engine.analyze_emotion(text_input)
            logger.info(f"[TEXT] Detected Emotion: {text_emotion} (Confidence: {confidence})")
            return text_emotion, confidence
        except Exception as e:
            logger.error(f"[TEXT FAILED] {e}")
            return "neutral", 0.0

    def analyze_context_emotion(self, context_data):
        """
        Analyze emotions from context-related memory search results.
        """
        try:
            if not context_data:
                logger.info("[CONTEXT] No relevant context found.")
                return "neutral", 0.0

            context_emotion, confidence = self.emotion_engine.contextual_emotion_analysis(
                text=" ".join([m["text"] for m in context_data]),
                context=[m["text"] for m in context_data]
            )
            logger.info(f"[CONTEXT] Detected Emotion: {context_emotion} (Confidence: {confidence})")
            return context_emotion, confidence
        except Exception as e:
            logger.error(f"[CONTEXT FAILED] {e}")
            return "neutral", 0.0

    def determine_final_emotion(
        self, visual_emotion, visual_confidence,
        text_emotion, text_confidence,
        context_emotion, context_confidence
    ):
        """
        Determine the final emotion based on the highest cumulative confidence score.
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