# thought_engine.py

import logging
from typing import Dict, List, Any

# Configure logging
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class ThoughtEngine:
    def __init__(self, db):
        """
        Initialize ThoughtEngine with a database interface.

        :param db: Database connector object with a method to run queries.
        """
        self.db = db

    def reflect(self, input_text: str) -> str:
        """
        Reflect on an input event by querying related memories and emotions from the database.

        :param input_text: The event text to reflect upon.
        :return: A string describing the memory and associated emotion or a message if no memory is found.
        """
        try:
            query = """
            MATCH (m:Memory {event: $event})-[:LINKED_TO]->(e:Emotion)
            RETURN m.event AS event, e.name AS emotion
            """
            result = self.db.run_query(query, {"event": input_text})
            if result:
                memory = result[0]
                message = f"Found memory of '{memory['event']}' with emotion '{memory['emotion']}'."
                logger.info(f"[REFLECT] {message}")
                return message
            else:
                message = f"No memory found for '{input_text}'."
                logger.info(f"[REFLECT] {message}")
                return message
        except Exception as e:
            logger.error(f"[REFLECT ERROR] Error reflecting on '{input_text}': {e}", exc_info=True)
            return "An error occurred while reflecting on the event."