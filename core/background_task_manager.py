# Background Task Manager for Maia AI
import threading
import time
import psutil  # For system monitoring
from backend.neo4j_connection import Neo4jConnection
from backend.memory_reinterpretation import MemoryReinterpretationEngine
from backend.reflective_journaling import ReflectiveJournaling
from backend.self_initiated_conversation import SelfInitiatedConversation

# Initialize Neo4j Connection
db = Neo4jConnection(
    uri="neo4j+s://46dc0ffd.databases.neo4j.io:7687",
    user="neo4j",
    password="4KjyYMe6ovQnU9QaRDnwP1q85Ok_rtB9l5p2yiWLgh8"
)

class BackgroundTaskManager:
    def __init__(self):
        self.active = True
        self.memory_engine = MemoryReinterpretationEngine()
        self.journal_engine = ReflectiveJournaling()
        self.conversation_engine = SelfInitiatedConversation()

    def resource_check(self):
        """
        Monitors CPU and memory usage to prevent system overload.
        """
        cpu_usage = psutil.cpu_percent()
        memory_usage = psutil.virtual_memory().percent
        return cpu_usage < 75 and memory_usage < 75  # Safe thresholds

    def introspection_cycle(self):
        """
        Periodically triggers memory reinterpretation.
        """
        while self.active:
            if self.resource_check():
                memory = self.memory_engine.retrieve_memory_for_reflection()
                if memory:
                    reinterpretation = self.memory_engine.reinterpret_memory(memory)
                    print(f"Introspection Result: {reinterpretation}")
            time.sleep(1800)  # Every 30 minutes
            
    def initiate_background_introspection(self):
        """
        Starts background memory linking and emotional evolution.
        """
        self.background_task_manager.run_introspective_tasks(interval=300)  # Every 5 mins
    
    def journaling_cycle(self):
        """
        Periodically triggers reflective journaling.
        """
        while self.active:
            if self.resource_check():
                self.journal_engine.log_event(
                    "Background Thought",
                    "I took a moment to reflect on recent events.",
                    "reflective"
                )
                print("Journal Entry Created.")
            time.sleep(3600)  # Every hour

    def conversation_cycle(self):
        """
        Triggers self-initiated conversations on unresolved queries.
        """
        while self.active:
            if self.resource_check():
                self.conversation_engine.check_emotional_triggers()
            time.sleep(900)  # Every 15 minutes

    def start(self):
        """
        Starts all background task threads.
        """
        threading.Thread(target=self.introspection_cycle, daemon=True).start()
        threading.Thread(target=self.journaling_cycle, daemon=True).start()
        threading.Thread(target=self.conversation_cycle, daemon=True).start()

# Test Function (Comment out in production)
if __name__ == "__main__":
    manager = BackgroundTaskManager()
    manager.start()

    print("Background tasks started. Press Ctrl+C to stop.")
    while True:
        time.sleep(1)