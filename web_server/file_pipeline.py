# Filename: /web_server/file_pipeline.py

from config.settings import CONFIG
from core.neo4j_connector import Neo4jConnector
from core.memory_engine import MemoryEngine
from file_parser import FileParser
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
        # Debug Environment Variables
        print("NEO4J_URI:", CONFIG["NEO4J_URI"])
        print("NEO4J_USER:", CONFIG["NEO4J_USER"])
        print("NEO4J_PASSWORD:", CONFIG["NEO4J_PASSWORD"])

        # Initialize Core Components
        self.neo4j = Neo4jConnector(
            CONFIG["NEO4J_URI"],
            CONFIG["NEO4J_USER"],
            CONFIG["NEO4J_PASSWORD"]
        )
        self.memory_engine = MemoryEngine(self.neo4j)
        self.file_parser = FileParser()
        self.model = None

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
            logger.info(f"Validated file MIME type: {mime_type}")

            # Parse File Content
            content = self.file_parser.parse(filepath)
            logger.info(f"File content parsed: {len(content)} characters.")

            # Analyze Content and Store Memory
            emotion = "neutral"  # Placeholder for actual emotion analysis
            self.memory_engine.store_memory(content, emotion)

            return {"mime_type": mime_type, "content_length": len(content), "emotion": emotion}

        except Exception as e:
            logger.error(f"Error processing file {filepath}: {e}")
            raise

    def process_mycelium_audio(self, audio_file):
        """
        Process audio files starting with 'Mycelium_'.
        Extract features, classify, and store them in memory.
        """
        try:
            features = extract_features(audio_file)

            # Train the classifier (or load a pre-trained model if available)
            if not self.model:
                # Dummy training data - replace with actual data
                X = np.random.rand(100, 3)  # Features
                y = np.random.randint(0, 2, 100)  # Labels
                self.model = train_classifier(X, y)

            # Predict Class (replace features with extracted ones)
            audio_features = [features["rms"], features["spectral_centroid"], features["zero_crossing_rate"]]
            prediction = self.model.predict([audio_features])[0]
            emotion_label = "Active" if prediction == 1 else "Calm"

            # Store in Memory
            self.memory_engine.store_memory(
                text=f"Mycelium Audio: {audio_file} classified as {emotion_label}",
                emotion=emotion_label.lower(),
                additional_data=features
            )

            return {
                "message": "Mycelium audio processed successfully!",
                "features": features,
                "classification": emotion_label,
                "status": "success"
            }
        except Exception as e:
            logger.error(f"Error processing Mycelium audio file {audio_file}: {e}")
            return {"message": f"Error processing audio file: {str(e)}", "status": "error"}
