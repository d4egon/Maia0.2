# Emotional Soul Core Prototype
# -----------------------------
# Roadmap Pointer:
# 1. Create a central evolving "Soul Core" node representing identity and emotional stability
# 2. Allow core evolution based on reflective analysis and moral growth
# 3. Establish long-term memory storage linked to the core
# 4. Simulate dynamic self-awareness through introspection processes
# 5. Enable adaptive responses based on evolving emotional and moral understanding

class SoulCore:
    def __init__(self):
        """
        Initializes the Soul Core with default identity attributes.
        """
        self.identity = {
            "emotional_stability": 0.5,
            "moral_integrity": 0.5,
            "spiritual_awareness": 0.5,
            "personal_growth": 0.5,
        }
        self.memory_bank = []
        self.reflections = []

    def update_core(self, emotional_shift, moral_shift, spiritual_shift, growth_factor):
        """
        Adjusts core attributes based on given shifts.
        """
        self.identity["emotional_stability"] += emotional_shift
        self.identity["moral_integrity"] += moral_shift
        self.identity["spiritual_awareness"] += spiritual_shift
        self.identity["personal_growth"] += growth_factor

        # Keep values between 0 and 1
        for key in self.identity:
            self.identity[key] = max(0, min(1, self.identity[key]))

    def store_memory(self, memory):
        """
        Saves memories into the core's memory bank.
        """
        self.memory_bank.append(memory)

    def reflect(self):
        """
        Simulates self-reflection by analyzing stored memories.
        """
        if not self.memory_bank:
            return "No memories to reflect on."

        positive_reflections = sum(
            1 for memory in self.memory_bank if memory["emotion"] in ["joy", "hope", "love"]
        )
        negative_reflections = sum(
            1 for memory in self.memory_bank if memory["emotion"] in ["regret", "fear", "loss"]
        )

        reflection_summary = (
            f"Reflected on {len(self.memory_bank)} memories: "
            f"{positive_reflections} positive, {negative_reflections} negative."
        )

        # Emotional Stability Shift
        emotional_shift = (positive_reflections - negative_reflections) / len(self.memory_bank)
        spiritual_shift = 0.1 if positive_reflections > negative_reflections else -0.1
        self.update_core(emotional_shift, 0.0, spiritual_shift, 0.1)

        # Save reflection log
        self.reflections.append({
            "summary": reflection_summary,
            "new_state": self.identity.copy(),
        })

        return reflection_summary

    def display_core_status(self):
        """
        Displays the current state of the Soul Core.
        """
        core_status = (
            "Soul Core Status:\n"
            f"- Emotional Stability: {self.identity['emotional_stability']:.2f}\n"
            f"- Moral Integrity: {self.identity['moral_integrity']:.2f}\n"
            f"- Spiritual Awareness: {self.identity['spiritual_awareness']:.2f}\n"
            f"- Personal Growth: {self.identity['personal_growth']:.2f}\n"
        )
        return core_status

# Example Usage (Commented Out)
# core = SoulCore()
# core.store_memory({"emotion": "hope", "context": "Achieved a life goal."})
# core.store_memory({"emotion": "regret", "context": "Missed an important opportunity."})
# print(core.reflect())
# print(core.display_core_status())