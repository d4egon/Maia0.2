# Filename: /web_server/file_pipeline.py

from config.settings import CONFIG
from core.neo4j_connector import Neo4jConnector
from core.memory_engine import MemoryEngine
from core.file_parser import FileParser
from audio_feature_extractor import extract_features
from signal_classifier import train_classifier
import numpy as np
import logging
import mimetypes
import os

# Set up logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

class FilePipeline:
    def __init__(self):
        # Initialize Core Components
        try:
            self.neo4j = Neo4jConnector(
                CONFIG["NEO4J_URI"],
                CONFIG["NEO4J_USER"],
                CONFIG["NEO4J_PASSWORD"]
            )
            self.memory_engine = MemoryEngine(self.neo4j)
            self.file_parser = FileParser()
            self.model = None
            logger.info("[INIT] FilePipeline initialized successfully.")
        except Exception as e:
            logger.critical(f"[INIT FAILED] Failed to initialize FilePipeline: {e}", exc_info=True)
            raise

    def process_file(self, filepath):
        filename = os.path.basename(filepath)

        # Handle Mycelium Audio Files
        if filename.lower().startswith("mycelium_") and filename.lower().endswith(".wav"):
            return self.process_mycelium_audio(filepath)

        try:
            # Validate MIME Type
            mime_type, _ = mimetypes.guess_type(filepath)
            if not mime_type:
                raise ValueError("Could not determine file MIME type.")
            logger.info(f"[VALIDATION] File MIME type validated: {mime_type}")

            # Parse File Content
            content = self.file_parser.parse(filepath)
            if not content.strip():
                raise ValueError("Parsed content is empty.")
            logger.info(f"[PARSING] File content parsed successfully ({len(content)} characters).")

            # Analyze Content and Store Memory
            emotion = "neutral"  # Placeholder for future emotion analysis integration
            self.memory_engine.store_memory(content, emotion)

            logger.info(f"[MEMORY] File '{filename}' stored in memory with emotion '{emotion}'.")
            return {
                "mime_type": mime_type,
                "content_length": len(content),
                "emotion": emotion,
                "status": "success"
            }
        except ValueError as ve:
            logger.warning(f"[WARNING] {ve}")
            return {"message": str(ve), "status": "warning"}
        except Exception as e:
            logger.error(f"[ERROR] Failed to process file '{filepath}': {e}", exc_info=True)
            return {"message": f"Error processing file: {e}", "status": "error"}

    def process_mycelium_audio(self, audio_file):
        """
        Process audio files starting with 'Mycelium_'.
        Extract features, classify, and store them in memory.
        """
        try:
            features = extract_features(audio_file)
            logger.info(f"[FEATURES] Audio features extracted: {features}")

            # Load or Train Classifier
            if not self.model:
                logger.info("[MODEL] No pre-trained model found. Training with dummy data...")
                X = np.random.rand(100, 3)  # Features
                y = np.random.randint(0, 2, 100)  # Labels
                self.model = train_classifier(X, y)
                logger.info("[MODEL] Classifier trained successfully.")

            # Predict Class
            audio_features = [features.get("rms", 0), 
                              features.get("spectral_centroid", 0), 
                              features.get("zero_crossing_rate", 0)]
            prediction = self.model.predict([audio_features])[0]
            emotion_label = "Active" if prediction == 1 else "Calm"

            # Store in Memory
            self.memory_engine.store_memory(
                text=f"Mycelium Audio: {os.path.basename(audio_file)} classified as {emotion_label}",
                emotion=emotion_label.lower(),
                additional_data=features
            )

            logger.info(f"[MEMORY] Audio '{audio_file}' classified as '{emotion_label}' and stored in memory.")
            return {
                "message": "Mycelium audio processed successfully!",
                "features": features,
                "classification": emotion_label,
                "status": "success"
            }
        except Exception as e:
            logger.error(f"[ERROR] Failed to process Mycelium audio file '{audio_file}': {e}", exc_info=True)
            return {"message": f"Error processing audio file: {str(e)}", "status": "error"}
