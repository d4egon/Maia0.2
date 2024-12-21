# /core/initialize_memories.py

import logging
from dotenv import load_dotenv
import os

from core.memory_engine import MemoryEngine
from core.neo4j_connector import Neo4jConnector

# Load environment variables
load_dotenv()

# Initialize logger
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

# Connect to Neo4j using credentials from .env
db = Neo4jConnector(
    uri=os.getenv("NEO4J_URI"),    # From .env
    user=os.getenv("NEO4J_USER"),  # From .env
    password=os.getenv("NEO4J_PASSWORD")  # From .env
)

# Correctly initialize the MemoryEngine class
memory_engine = MemoryEngine(db)


def initialize_memories():
    """Insert foundational memories into Neo4j."""
    logger.info("[INITIALIZATION START] Inserting foundational memories...")

    # List of foundational memories
    memories = [
        # Greetings & Introductions
        ("hello", ["happy", "curious"], "General greeting", "Greeting", "High", "Blue"),
        ("good morning", ["happy", "energetic"], "Morning greeting", "Greeting", "High", "Yellow"),
        ("who are you?", ["curious"], "Query about identity", "Introduction", "High", "Purple"),

        # Emotions & Feelings
        ("i am happy", ["happy"], "User expresses happiness", "Emotion", "Medium", "Green"),
        ("i feel sad", ["sad"], "User expresses sadness", "Emotion", "Medium", "Gray"),
        ("i am excited", ["excited"], "User expresses excitement", "Emotion", "High", "Orange"),

        # Affirmations & Responses
        ("yes", ["affirming"], "Affirmative response", "Response", "Medium", "Cyan"),
        ("no", ["neutral"], "Negative response", "Response", "Medium", "Gray"),
        ("thank you", ["grateful"], "Expression of gratitude", "Response", "High", "Gold"),

        # Ethical Principles & Guidance
        ("be kind to others", ["compassion"], "Guiding principle about kindness", "Ethical Principle", "High", "Purple"),
        ("help those in need", ["compassion"], "Moral responsibility toward others", "Ethical Principle", "High", "Purple"),
        ("tell the truth", ["integrity"], "Honesty and truthfulness", "Ethical Principle", "High", "Blue"),

        # Inspirational Quotes & Scriptures
        ("The Lord is my shepherd, I shall not want.", ["peaceful", "hopeful"], "Encouraging Biblical verse", "Scripture", "High", "Gold"),
        ("I can do all things through Christ who strengthens me.", ["inspired", "hopeful"], "Encouraging Biblical verse", "Scripture", "High", "Gold")
    ]

    # Insert all memories
    for text, emotions, description, memory_type, importance, color in memories:
        try:
            memory_engine.store_memory(
                text=text,
                emotions=emotions,
                extra_properties={
                    "description": description,
                    "type": memory_type,
                    "importance": importance,
                    "color": color
                }
            )
            logger.info(f"[MEMORY INSERTED] '{text}' stored successfully.")
        except Exception as e:
            logger.error(f"[INSERTION FAILED] '{text}' could not be stored: {e}", exc_info=True)

    logger.info("[INITIALIZATION COMPLETE] Foundational memories inserted.")


if __name__ == "__main__":
    initialize_memories()
