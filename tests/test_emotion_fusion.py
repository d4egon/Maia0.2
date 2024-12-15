# Filename: /tests/test_emotion_fusion.py

import os
import traceback
from core.emotion_fusion_engine import EmotionFusionEngine
from core.memory_engine import MemoryEngine
from core.neo4j_connector import Neo4jConnector
from NLP.nlp_engine import NLP
from config.settings import CONFIG

def initialize_core_services():
    """
    Initialize Neo4j connection and core services.
    """
    neo4j = Neo4jConnector(
        CONFIG["NEO4J_URI"], 
        CONFIG["NEO4J_USER"], 
        CONFIG["NEO4J_PASSWORD"]
    )
    memory_engine = MemoryEngine(neo4j)
    nlp_engine = NLP(None, None, None)
    emotion_engine = EmotionFusionEngine(nlp_engine, memory_engine)
    return neo4j, emotion_engine

def analyze_emotions(emotion_engine, dataset_base_path):
    """
    Analyze all emotions and run tests.
    """
    emotions = ["angry", "disgust", "fear", "happy", "neutral", "sad", "surprise"]

    for emotion in emotions:
        emotion_folder = os.path.join(dataset_base_path, emotion)

        if not os.path.exists(emotion_folder):
            print(f"[WARNING] Folder does not exist: {emotion_folder}")
            continue

        image_files = os.listdir(emotion_folder)
        if not image_files:
            print(f"[WARNING] No files found in folder: {emotion_folder}")
            continue

        # Use the first image in the folder for testing
        sample_image = os.path.join(emotion_folder, image_files[0])
        text_input = f"This is an example of {emotion} emotion."

        try:
            # Perform emotion fusion with confidence logging
            result = emotion_engine.fuse_emotions(sample_image, text_input)
            print(f"[SUCCESS] Test Result for {emotion}: {result}")
        except Exception as e:
            print(f"[ERROR] Error analyzing {emotion}: {e}")
            traceback.print_exc()

def main():
    """
    Main test execution.
    """
    dataset_base_path = "dataset/test"

    # Initialize services
    neo4j, emotion_engine = initialize_core_services()

    try:
        # Run emotion analysis tests
        analyze_emotions(emotion_engine, dataset_base_path)
    finally:
        neo4j.close()
        print("[INFO] Test completed and Neo4j connection closed.")

if __name__ == "__main__":
    main()