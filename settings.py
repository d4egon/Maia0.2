# settings.py - Configuration Settings

# Flask Configuration
DEBUG = True
SECRET_KEY = "FungiFungi"

# Database Configuration
SQLITE_DB_PATH = "data/maia_emotion_db.db"
NEO4J_URI = "bolt://localhost:7687"
NEO4J_USERNAME = "neo4j"
NEO4J_PASSWORD = "4KjyYMe6ovQnU9QaRDnwP1q85Ok_rtB9l5p2yiWLgh8"

# Model Paths
MODEL_PATH = "backend/emotion_recognition_model.h5"
