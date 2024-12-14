import sys
import os

# Add the project root directory to the Python Path
sys.path.append(os.path.abspath(os.path.dirname(__file__) + '/../'))

# Debug the Python Path
print("Python Path:", sys.path)

# Correct Path Check
print("Backend Path Exists:", os.path.exists(os.path.abspath(os.path.dirname(__file__) + '/../backend')))

# Correct Imports
from backend.recursive_thought_engine import RecursiveThoughtEngine
from backend.emotional_behavior_engine import EmotionalBehaviorEngine

# Initialize Engines
rte = RecursiveThoughtEngine()
ebe = EmotionalBehaviorEngine()

def test_recursive_thoughts():
    """
    Test the Recursive Thought Engine with a sample memory.
    """
    print("\n=== Testing Recursive Thought Engine ===")
    introspection_result = rte.reflect_recursively("First Memory")
    print("Recursive Thought Output:")
    print(introspection_result)

def test_emotional_behavior():
    """
    Test the Emotional Behavior Engine with a simulated context.
    """
    print("\n=== Testing Emotional Behavior Engine ===")
    current_behavior = ebe.generate_behavioral_response("Reflective Query")
    print("Emotional Behavior Response:")
    print(current_behavior)

def run_tests():
    """
    Runs all tests for RTE and EBE.
    """
    print("Starting Dynamic Testing for RTE and EBE...")
    test_recursive_thoughts()
    test_emotional_behavior()
    print("\nAll tests completed.")

if __name__ == "__main__":
    run_tests()