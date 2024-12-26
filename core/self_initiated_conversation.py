# self_initiated_conversation.py - Autonomous Conversations
import schedule
import time
import random
import threading
import logging
from typing import List, Dict


logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class SelfInitiatedConversation:
    def __init__(self, memory_engine, conversation_engine, socketio):
        """
        Initialize the SelfInitiatedConversation with necessary components.

        :param memory_engine: An instance for managing memories.
        :param conversation_engine: An instance for processing conversation logic.
        :param socketio: Socket.IO server for real-time communication.
        """
        self.memory_engine = memory_engine
        self.conversation_engine = conversation_engine
        self.socketio = socketio

    def start_scheduler(self):
        """
        Start the scheduler for autonomous conversation triggers.
        """
        logger.info("[SCHEDULER START] Initiating autonomous conversation scheduler...")
        schedule.every().hour.do(self.trigger_reflection)
        schedule.every(30).minutes.do(self.trigger_conversation_start)
        threading.Thread(target=self.run_scheduler, daemon=True).start()

    def run_scheduler(self):
        """
        Run the scheduler in a loop to execute pending jobs.
        """
        while True:
            try:
                schedule.run_pending()
                time.sleep(1)
            except Exception as e:
                logger.error(f"[SCHEDULER ERROR] {e}", exc_info=True)

    def trigger_reflection(self):
        """
        Trigger reflection by discussing top retrieved memories.
        """
        try:
            top_memories = self.memory_engine.get_top_retrieved_memories(limit=3)
            for memory in top_memories:
                response = self.conversation_engine.process_user_input(memory['text'])
                logger.info(f"[AUTONOMOUS REFLECTION] {response}")
                self.socketio.emit("new_message", {"message": response}, broadcast=True)
        except Exception as e:
            logger.error(f"[REFLECTION TRIGGER ERROR] {e}", exc_info=True)

    def trigger_conversation_start(self):
        """
        Initiate a new conversation with a random prompt.
        """
        prompts: List[str] = [
            "What have you been thinking about lately?",
            "Would you like to reflect on something together?",
            "Is there anything on your mind you'd like to explore?"
        ]
        try:
            chosen_prompt = random.choice(prompts)
            response = self.conversation_engine.process_user_input(chosen_prompt)
            logger.info(f"[AUTONOMOUS STARTER] {response}")
            self.socketio.emit("new_message", {"message": response}, broadcast=True)
        except Exception as e:
            logger.error(f"[CONVERSATION START ERROR] {e}", exc_info=True)