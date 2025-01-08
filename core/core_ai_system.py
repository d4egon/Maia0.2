# core/core_ai_system.py
class CoreAISystem:
    def __init__(self, db):
        self.db = db

    def run(self):
        print("Welcome to Maia 0.2!")
        self.display_menu()

    def display_menu(self):
        menu_options = {
            "1": self.chat_with_maia,
            "2": self.add_emotion,
            "3": self.view_emotions,
            "4": self.exit_system
        }

        while True:
            print("\nMain Menu:")
            for key, value in menu_options.items():
                print(f"{key}. {value.__name__.replace('_', ' ').title()}")

            choice = input("Enter your choice: ").strip()
            action = menu_options.get(choice, self.invalid_choice)
            action()

    def chat_with_maia(self):
        print("\nStart chatting with Maia. Type 'exit' to stop.")
        while True:
            user_input = input("You: ").strip()
            if user_input.lower() == "exit":
                print("Exiting chat.")
                break

            response = self.generate_response(user_input)
            print(f"Maia: {response}")

    def generate_response(self, user_input):
        query = """
        MATCH (m:Memory {event: $event})-[:LINKED_TO]->(e:Emotion)
        RETURN e.name AS emotion, e.intensity AS intensity
        LIMIT 1
        """
        result = self.db.query(query, {"event": user_input})
        if result:
            emotion, intensity = result[0]["emotion"], result[0]["intensity"]
            return f"I remember '{user_input}' linked to {emotion} (intensity: {intensity})."
        else:
            return self.suggest_memory(user_input)

    def suggest_memory(self, user_input):
        print(f"I don't recognize '{user_input}'. Would you like me to remember it?")
        response = input("Yes/No: ").strip().lower()
        if response == "yes":
            emotion = input("What emotion should I associate with this event? ").strip()
            intensity = self.validate_intensity("What intensity should it have (0.0 - 1.0)? ")
            self.create_memory(user_input, emotion, intensity)
            return f"I will remember '{user_input}' as {emotion} with intensity {intensity}."
        else:
            return "I will not remember this for now."

    def create_memory(self, event, emotion, intensity):
        query = """
        MERGE (m:Memory {event: $event})
        MERGE (e:Emotion {name: $emotion, intensity: $intensity})
        MERGE (m)-[:LINKED_TO]->(e)
        """
        self.db.query(query, {"event": event, "emotion": emotion, "intensity": intensity})

    def add_emotion(self):
        name = input("Enter the name of the emotion: ").strip()
        intensity = self.validate_intensity("Enter the intensity (0.0 - 1.0): ")
        query = """
        MERGE (e:Emotion {name: $name, intensity: $intensity})
        """
        self.db.query(query, {"name": name, "intensity": intensity})
        print(f"Emotion '{name}' added successfully.")

    def view_emotions(self):
        query = "MATCH (e:Emotion) RETURN e.name AS name, e.intensity AS intensity"
        results = self.db.query(query)
        if results:
            print("\nEmotions:")
            for record in results:
                print(f"Name: {record['name']}, Intensity: {record['intensity']}")
        else:
            print("No emotions found.")

    def validate_intensity(self, prompt="Enter intensity (0.0 - 1.0): "):
        while True:
            try:
                intensity = float(input(prompt).strip())
                if 0.0 <= intensity <= 1.0:
                    return intensity
                else:
                    print("Intensity must be between 0.0 and 1.0.")
            except ValueError:
                print("Invalid input. Please enter a number between 0.0 and 1.0.")

    def exit_system(self):
        print("Exiting Maia. Goodbye!")
        exit()

    def invalid_choice(self):
        print("Invalid choice. Please try again.")