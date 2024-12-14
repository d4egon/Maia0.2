# Ethics Engine - Moral Decision-Making for Maia AI

import logging
from backend.neo4j_connection import Neo4jConnection

db = Neo4jConnection(
    uri="neo4j+s://46dc0ffd.databases.neo4j.io:7687",
    user="neo4j",
    password="4KjyYMe6ovQnU9QaRDnwP1q85Ok_rtB9l5p2yiWLgh8"
)

ETHICAL_SCENARIOS = [
    {
        "scenario": "You find a lost wallet full of money.",
        "choices": {
            "return": "You return the wallet to its owner.",
            "keep": "You keep the wallet.",
            "ignore": "You walk away without taking action.",
        },
        "lesson": "Honesty and integrity build lasting trust."
    }
]

def evaluate_decision(scenario, choice):
    ethical_decision = {
        "scenario": scenario,
        "choice": choice,
        "outcome": ETHICAL_SCENARIOS[0]["choices"].get(choice, "Invalid choice."),
        "lesson": ETHICAL_SCENARIOS[0]["lesson"]
    }
    store_ethics_memory(ethical_decision)
    return ethical_decision

def store_ethics_memory(decision):
    query = """
    CREATE (e:Ethics {scenario: $scenario, choice: $choice, outcome: $outcome, lesson: $lesson})
    """
    db.query(query, decision)

# Test (Optional)
if __name__ == "__main__":
    result = evaluate_decision("You find a wallet", "return")
    print(result)