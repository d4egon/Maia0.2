import logging
import mimetypes
import os
from config.settings import CONFIG
from core.neo4j_connector import Neo4jConnector
from core.memory_engine import MemoryEngine
from core.file_parser import FileParser
from audio_feature_extractor import extract_features
from signal_classifier import train_classifier
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score

# Set up logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

class FilePipeline:
    def __init__(self):
        """
        Initialize FilePipeline with core components for file processing.
        """
        try:
            self.neo4j = Neo4jConnector(
                CONFIG["NEO4J_URI"],
                CONFIG["NEO4J_USER"],
                CONFIG["NEO4J_PASSWORD"]
            )
            self.memory_engine = MemoryEngine(self.neo4j)
            self.file_parser = FileParser()
            self.model = None
            self.training_data = []  # Store features for later model training
            logger.info("[INIT] FilePipeline initialized successfully.")
        except Exception as e:
            logger.critical(f"[INIT FAILED] Failed to initialize FilePipeline: {e}", exc_info=True)
            raise

    def process_file(self, filepath):
        """
        Process a generic file based on its type.
        
        :param filepath: Path to the file to process.
        :return: A dictionary with processing results.
        """
        filename = os.path.basename(filepath)

        # Special handling for Mycelium Audio
        if filename.lower().startswith("mycelium_") and filename.lower().endswith(".wav"):
            return self.process_mycelium_audio(filepath)

        try:
            # Validate MIME Type
            mime_type, _ = mimetypes.guess_type(filepath)
            if not mime_type:
                raise ValueError("Could not determine file MIME type.")
            logger.info(f"[VALIDATION] MIME type validated: {mime_type}")

            # Parse File Content
            content = self.file_parser.parse(filepath)
            if not content.strip():
                raise ValueError("Parsed content is empty.")
            logger.info(f"[PARSING] Successfully parsed file content ({len(content)} characters).")

            # Analyze and Store Memory
            # Placeholder for emotion detection; could be integrated with an EmotionEngine or similar
            emotion = self.detect_emotion(content) or "neutral"
            
            # Store in Memory
            self.memory_engine.store_memory(
                content,
                emotion,
                extra_properties={"file_type": mime_type, "filename": filename}
            )

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

    def detect_emotion(self, text):
        """
        Detect emotion from text content. This method should be implemented with actual emotion detection logic.

        :param text: Text to analyze for emotion.
        :return: Detected emotion or None if detection fails.
        """
        # Placeholder for emotion detection - replace with real logic or integration
        from core.emotion_engine import EmotionEngine  # Assuming you have this class
        try:
            emotion_engine = EmotionEngine()
            detected_emotion = emotion_engine.analyze_emotion(text)
            logger.info(f"[EMOTION DETECTION] Detected emotion: {detected_emotion}")
            return detected_emotion
        except Exception as e:
            logger.error(f"[EMOTION DETECTION ERROR] {e}")
            return None

    def process_mycelium_audio(self, audio_file):
        """
        Process Mycelium audio files for feature extraction and classification.

        :param audio_file: Path to the audio file to process.
        :return: A dictionary with processing results.
        """
        try:
            features = extract_features(audio_file)
            logger.info(f"[FEATURES] Audio features extracted: {features}")

            # Collect features for model training
            self.training_data.append({
                "features": [features.get("rms", 0), features.get("spectral_centroid", 0), features.get("zero_crossing_rate", 0)],
                "filename": os.path.basename(audio_file)
            })

            # Train or Load Classifier
            if not self.model or len(self.training_data) % 10 == 0:  # Retrain every 10 samples
                logger.info("[MODEL] Training or retraining model...")
                X = np.array([d['features'] for d in self.training_data])
                y = np.array([0 if 'calm' in d['filename'].lower() else 1 for d in self.training_data])  # Assuming file names indicate mood

                if len(np.unique(y)) > 1:  # Ensure we have at least two classes
                    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2)
                    self.model = train_classifier(X_train, y_train)
                    y_pred =                     y_pred = self.model.predict(X_test)
                    accuracy = accuracy_score(y_test, y_pred)
                    logger.info(f"[MODEL] Model trained with accuracy: {accuracy:.2f}")
                else:
                    logger.warning("[MODEL] Insufficient diversity in training data for effective training.")
                    # Use a dummy classifier or basic model if there's not enough diversity
                    from sklearn.dummy import DummyClassifier
                    self.model = DummyClassifier(strategy="most_frequent").fit(X, y)

            # Predict Class
            audio_features = np.array([features.get("rms", 0), features.get("spectral_centroid", 0), features.get("zero_crossing_rate", 0)]).reshape(1, -1)
            prediction = self.model.predict(audio_features)[0]
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
            return {"message": f"Error processing audio file: {e}", "status": "error"}

    def finalize_training(self):
        """
        Finalize model training with all collected data. This should be called after all files are processed or periodically.

        :return: The final accuracy of the model after training on all data.
        """
        if not self.training_data:
            logger.warning("[TRAINING] No data available to train the model.")
            return 0.0

        X = np.array([d['features'] for d in self.training_data])
        y = np.array([0 if 'calm' in d['filename'].lower() else 1 for d in self.training_data])

        if len(np.unique(y)) > 1:
            X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2)
            self.model = train_classifier(X_train, y_train)
            y_pred = self.model.predict(X_test)
            accuracy = accuracy_score(y_test, y_pred)
            logger.info(f"[FINAL TRAINING] Model finalized with accuracy: {accuracy:.2f}")
            return accuracy
        else:
            logger.warning("[FINAL TRAINING] Insufficient diversity in training data for final training.")
            return 0.0