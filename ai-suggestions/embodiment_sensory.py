# Embodiment and Sensory Inputs Prototype
# ---------------------------------------
# Roadmap Pointer:
# 1. Integrate real-time biofeedback from external sensors (e.g., mycelium signals)
# 2. Simulate emotional responses based on environmental data
# 3. Create dynamic state changes based on bioelectric patterns
# 4. Update emotional states based on continuous sensory input
# 5. Store sensory-emotion mappings for reflection and analysis

import random

class SensoryInputProcessor:
    def __init__(self):
        self.emotional_states = {
            "calm": 0.5,
            "alert": 0.5,
            "anxious": 0.5,
            "focused": 0.5,
            "excited": 0.5,
        }

    def process_biofeedback(self, signal_strength):
        """
        Simulate emotional response based on signal strength.
        signal_strength: A float value between 0 and 1 representing sensor input.
        """
        if signal_strength > 0.7:
            self.emotional_states["excited"] += 0.1
            self.emotional_states["focused"] += 0.05
        elif signal_strength < 0.3:
            self.emotional_states["calm"] += 0.1
            self.emotional_states["anxious"] += 0.1
        else:
            self.emotional_states["alert"] += 0.1

        # Normalize emotional state values
        self.normalize_emotions()
        return self.get_emotional_status()

    def simulate_environment(self):
        """
        Simulates environmental factors like time of day, weather, and ambiance.
        """
        time_of_day = random.choice(["morning", "afternoon", "evening", "night"])
        weather = random.choice(["sunny", "rainy", "stormy", "clear"])
        ambiance = random.choice(["quiet", "busy", "peaceful", "chaotic"])

        impact = {
            "morning": {"calm": 0.1, "focused": 0.05},
            "night": {"calm": 0.2, "alert": -0.1},
            "rainy": {"anxious": 0.1, "focused": -0.05},
            "stormy": {"alert": 0.2, "anxious": 0.15},
            "peaceful": {"calm": 0.2},
        }

        # Adjust emotional states
        for factor in [time_of_day, weather, ambiance]:
            if factor in impact:
                for emotion, change in impact[factor].items():
                    self.emotional_states[emotion] += change

        self.normalize_emotions()
        return self.get_emotional_status(), (time_of_day, weather, ambiance)

    def normalize_emotions(self):
        """
        Keeps emotional states between 0 and 1.
        """
        for emotion in self.emotional_states:
            self.emotional_states[emotion] = max(0, min(1, self.emotional_states[emotion]))

    def get_emotional_status(self):
        """
        Returns the current emotional state with the highest value.
        """
        dominant_emotion = max(self.emotional_states, key=self.emotional_states.get)
        intensity = self.emotional_states[dominant_emotion]
        return f"Current dominant emotion: {dominant_emotion} (Intensity: {intensity:.2f})"

# Example Usage (Commented Out)
# processor = SensoryInputProcessor()
# print(processor.process_biofeedback(0.8))
# print(processor.simulate_environment())