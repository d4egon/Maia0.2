# Filename: main.py

from config.settings import CONFIG
from core.neo4j_connector import Neo4jConnector
from core.memory_engine import MemoryEngine
from NLP.response_generator import ResponseGenerator
from NLP.nlp_engine import NLP
from core.self_initiated_conversation import SelfInitiatedConversation

import subprocess
from threading import Thread

from core.memory_linker import MemoryLinker

from core.context_search import ContextSearchEngine

# Initialize Context Search Engine
context_search_engine = ContextSearchEngine(neo4j)

# Enhance NLP Engine with Context Search
nlp_engine.attach_context_search(context_search_engine)

# Initialize Memory Linker
memory_linker = MemoryLinker(neo4j)

# Schedule Memory Linking every 5 minutes
import time
from threading import Thread

def scheduled_linking():
    while True:
        memory_linker.run_periodic_linking()
        time.sleep(300)  # Every 5 minutes

# Start Background Task
linking_thread = Thread(target=scheduled_linking, daemon=True)
linking_thread.start()

def run_web_server():
    subprocess.Popen(["python", "web_server/app.py"])

# Launch Flask server in a background thread
print("Launching upload service at http://127.0.0.1:5000 /n")
web_thread = Thread(target=run_web_server)
web_thread.start()

# Initialize Database Connection
print("Connecting to Neo4j AuraDB...")
neo4j = Neo4jConnector(CONFIG["NEO4J_URI"], CONFIG["NEO4J_USER"], CONFIG["NEO4J_PASS"])

# Initialize Core Modules
memory_engine = MemoryEngine(neo4j)
response_gen = ResponseGenerator(memory_engine, neo4j)
nlp_engine = NLP(memory_engine, response_gen, neo4j)
self_reflector = SelfInitiatedConversation(memory_engine, response_gen, neo4j)

# Database Cleanup
memory_engine.cleanup_database()
print("Database cleanup complete...")

def main():
    print("Welcome to Maia 0.2")
    print("Type 'exit' anytime to quit.\n")

    awaiting_feedback = False
    last_memory_text = ""

    while True:
        # User Input
        user_input = input("You: ").strip()

        if user_input.lower() == "exit":
            print("Goodbye! See you next time.")
            break

        # Handle Feedback
        if awaiting_feedback:
            if user_input.lower() in ["yes", "no"]:
                adjustment = 1 if user_input.lower() == "yes" else -1
                memory_engine.adjust_memory_weight(last_memory_text, adjustment)
                print("Maia: Thank you! I've updated my understanding.")
                awaiting_feedback = False
                continue

        # Process the input and generate response
        response = nlp_engine.process(user_input)
        print(f"Maia: {response}")

        # Check for feedback request in the response
        if "Was my interpretation accurate?" in response:
            awaiting_feedback = True
            last_memory_text = user_input

        # Trigger Self-Reflection
        reflection = self_reflector.generate_unprompted_message()
        if reflection:
            print(f"\n[Maia Thinking...]: {reflection}\n")

if __name__ == "__main__":
    main()