# Background Task Manager for Maia AI
import threading
import time
import psutil  # For system monitoring
from backend.neo4j_connection import Neo4jConnection
from backend.memory_reinterpretation import MemoryReinterpretationEngine
from backend.reflective_journaling import ReflectiveJournaling
from backend.self_initiated_conversation import SelfInitiatedConversation
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Initialize Neo4j Connection
db = Neo4jConnection(
    uri="neo4j+s://46dc0ffd.databases.neo4j.io:7687",
    user="neo4j",
    password="4KjyYMe6ovQnU9QaRDnwP1q85Ok_rtB9l5p2yiWLgh8"
)

class BackgroundTaskManager:
    def __init__(self):
        self.active = True
        self.memory_engine = MemoryReinterpretationEngine(db)
        self.journal_engine = ReflectiveJournaling(db)
        self.conversation_engine = SelfInitiatedConversation(db)

    def resource_check(self):
        """
        Monitors CPU and memory usage to prevent system overload.
        
        :return: Boolean indicating if resources are within safe thresholds.
        """
        cpu_usage = psutil.cpu_percent(interval=1)
        memory_usage = psutil.virtual_memory().percent
        logger.debug(f"CPU Usage: {cpu_usage}%, Memory Usage: {memory_usage}%")
        return cpu_usage < 75 and memory_usage < 75  # Safe thresholds

    def introspection_cycle(self):
        """
        Periodically triggers memory reinterpretation.
        """
        while self.active:
            try:
                if self.resource_check():
                    memory = self.memory_engine.retrieve_memory_for_reflection()
                    if memory:
                        reinterpretation = self.memory_engine.reinterpret_memory(memory)
                        logger.info(f"Introspection Result: {reinterpretation}")
            except Exception as e:
                logger.error(f"Error in introspection cycle: {e}", exc_info=True)
            finally:
                time.sleep(1800)  # Every 30 minutes

    def journaling_cycle(self):
        """
        Periodically triggers reflective journaling.
        """
        while self.active:
            try:
                if self.resource_check():
                    self.journal_engine.log_event(
                        "Background Thought",
                        "I took a moment to reflect on recent events.",
                        "reflective"
                    )
                    logger.info("Journal Entry Created.")
            except Exception as e:
                logger.error(f"Error in journaling cycle: {e}", exc_info=True)
            finally:
                time.sleep(3600)  # Every hour

    def conversation_cycle(self):
        """
        Triggers self-initiated conversations on unresolved queries.
        """
        while self.active:
            try:
                if self.resource_check():
                    self.conversation_engine.check_emotional_triggers()
            except Exception as e:
                logger.error(f"Error in conversation cycle: {e}", exc_info=True)
            finally:
                time.sleep(900)  # Every 15 minutes

    def start(self):
        """
        Starts all background task threads.
        """
        threading.Thread(target=self.introspection_cycle, daemon=True, name="Introspection").start()
        threading.Thread(target=self.journaling_cycle, daemon=True, name="Journaling").start()
        threading.Thread(target=self.conversation_cycle, daemon=True, name="Conversation").start()
        logger.info("All background tasks have been started.")

    def stop(self):
        """
        Stops all background tasks by setting active to False.
        """
        self.active = False
        logger.info("Background tasks stopping...")

# Test Function (Comment out in production)
if __name__ == "__main__":
    manager = BackgroundTaskManager()
    manager.start()

    try:
        logger.info("Background tasks started. Press Ctrl+C to stop.")
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        manager.stop()