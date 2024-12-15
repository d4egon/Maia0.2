# Filename: /core/ethics_engine.py

import logging
from core.neo4j_connector import Neo4jConnector

# Initialize logging
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

class EthicsEngine:
    def __init__(self, db: Neo4jConnector):
        self.db = db

    def evaluate_decision(self, scenario, choice):
        """
        Evaluate an ethical decision based on predefined scenarios and dynamic context analysis.
        """
        logger.info(f"[EVALUATION] Evaluating scenario: {scenario}, Choice: {choice}")

        # Retrieve Ethical Scenario
        ethical_scenario = self.get_scenario(scenario)

        if not ethical_scenario:
            logger.error(f"[EVALUATION FAILED] Scenario not found: {scenario}")
            return {"error": "Scenario not found."}

        # Analyze Choice
        outcome = ethical_scenario["choices"].get(choice, "Invalid choice.")
        lesson = ethical_scenario["lesson"]

        # Store Decision in Memory
        ethical_decision = {
            "scenario": scenario,
            "choice": choice,
            "outcome": outcome,
            "lesson": lesson,
        }
        self.store_ethics_memory(ethical_decision)

        logger.info(f"[EVALUATION RESULT] {ethical_decision}")
        return ethical_decision

    def get_scenario(self, scenario_text):
        """
        Retrieve predefined ethical scenarios from the database or built-in list.
        """
        query = """
        MATCH (e:EthicsScenario {scenario: $scenario_text})
        RETURN e.scenario AS scenario, e.choices AS choices, e.lesson AS lesson
        """
        result = self.db.run_query(query, {"scenario_text": scenario_text})

        if result:
            logger.debug(f"[SCENARIO FOUND] {result[0]}")
            return result[0]

        # Fallback to Predefined Scenarios
        predefined_scenarios = {
            "You find a lost wallet full of money.": {
                "choices": {
                    "return": "You return the wallet to its owner.",
                    "keep": "You keep the wallet.",
                    "ignore": "You walk away without taking action.",
                },
                "lesson": "Honesty and integrity build lasting trust.",
            }
        }
        return predefined_scenarios.get(scenario_text)

    def store_ethics_memory(self, decision):
        """
        Store ethical decisions in the memory database.
        """
        query = """
        CREATE (e:Ethics {scenario: $scenario, choice: $choice, outcome: $outcome, lesson: $lesson})
        """
        self.db.run_query(query, decision)
        logger.info(f"[MEMORY STORED] Ethical decision stored: {decision}")
