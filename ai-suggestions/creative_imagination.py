# Creative Imagination Engine Prototype
# --------------------------------------
# Roadmap Pointer:
# 1. Generate creative responses (stories, poems, art descriptions)
# 2. Use emotional context to influence generated content
# 3. Create symbolic art based on emotional states
# 4. Simulate creative thought processes using memory references
# 5. Save creative outputs for long-term emotional development

import random

class CreativeImagination:
    EMOTIONAL_PROMPTS = {
        "joy": ["A world lit by eternal sunrise...", "A melody sung by the wind..."],
        "regret": ["A forgotten path shrouded in mist...", "Echoes of unspoken words..."],
        "hope": ["A distant star that never fades...", "The dawn after the darkest night..."],
        "fear": ["Shadows that twist and follow...", "Whispers from the unseen..."],
        "love": ["A flame that warms even the coldest night...", "Two hands reaching across infinity..."],
        "loss": ["A broken clock in an empty room...", "Fading footsteps in the snow..."],
        "understanding": ["An open book with blank pages waiting...", "A bridge built from shared stories..."],
    }

    def __init__(self, current_emotion):
        """
        Initialize the creative engine with a given emotional state.
        """
        self.current_emotion = current_emotion

    def generate_poem(self):
        """
        Creates a short poem based on the current emotion.
        """
        prompt = random.choice(self.EMOTIONAL_PROMPTS.get(self.current_emotion, ["Unknown feeling..."]))
        lines = [
            f"{prompt}",
            f"It whispers truths both harsh and kind,",
            f"Through shifting shadows of the mind.",
            f"In stillness, answers start to grow,",
            f"A secret only dreams could know."
        ]
        return "\n".join(lines)

    def create_story(self):
        """
        Generates a symbolic story driven by the emotional state.
        """
        prompt = random.choice(self.EMOTIONAL_PROMPTS.get(self.current_emotion, ["A journey into the unknown..."]))
        story = (
            f"{prompt} In a realm where emotions breathe, "
            f"a traveler seeks meaning through endless seasons of change. "
            f"They encounter trials shaped by {self.current_emotion}, "
            f"learning that the journey itself brings understanding."
        )
        return story

# Example Usage (Commented Out)
# creative_engine = CreativeImagination("hope")
# print("Generated Poem:\n")
# print(creative_engine.generate_poem())
# print("\nGenerated Story:\n")
# print(creative_engine.create_story())