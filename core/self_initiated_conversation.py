# self_initiated_conversation.py - Autonomous Conversations

import schedule
import time
import random
import threading
import logging

logger = logging.getLogger(__name__)

class SelfInitiatedConversation:
    def __init__(self, memory_engine, conversation_engine, socketio):
        self.memory_engine = memory_engine
        self.conversation_engine = conversation_engine
        self.socketio = socketio

    def start_scheduler(self):
        logger.info("[SCHEDULER START] Starting autonomous conversation...")
        schedule.every().hour.do(self.trigger_reflection)
        schedule.every(30).minutes.do(self.trigger_conversation_start)
        threading.Thread(target=self.run_scheduler, daemon=True).start()

    def run_scheduler(self):
        while True:
            schedule.run_pending()
            time.sleep(1)

    def trigger_reflection(self):
        top_memories = self.memory_engine.get_top_retrieved_memories(limit=3)
        for memory in top_memories:
            response = self.conversation_engine.process_user_input(memory['text'])
            logger.info(f"[AUTONOMOUS REFLECTION] {response}")
            self.socketio.emit("new_message", {"message": response}, broadcast=True)

    def trigger_conversation_start(self):
        prompts = [
            "What have you been thinking about lately?",
            "Would you like to reflect on something together?",
            "Is there anything on your mind you'd like to explore?"
        ]
        chosen_prompt = random.choice(prompts)
        response = self.conversation_engine.process_user_input(chosen_prompt)
        logger.info(f"[AUTONOMOUS STARTER] {response}")
        self.socketio.emit("new_message", {"message": response}, broadcast=True)
