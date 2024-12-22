# Filename: /core/ethics_engine.py

import logging
from typing import Dict, Any
from core.neo4j_connector import Neo4jConnector

# Configure logging
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class EthicsEngine:
    def __init__(self, db: Neo4jConnector):
        """
        Initialize EthicsEngine with a database connector.

        :param db: An instance of Neo4jConnector for database operations.
        """
        self.db = db

    def evaluate_decision(self, scenario: str, choice: str) -> Dict[str, Any]:
        """
        Evaluate an ethical decision based on predefined scenarios and dynamic context analysis.

        :param scenario: Text describing the ethical scenario to evaluate.
        :param choice: The choice made within the scenario.
        :return: Dictionary containing the evaluation results or error message.
        """
        logger.info(f"[EVALUATION] Evaluating scenario: {scenario}, Choice: {choice}")

        try:
            # Retrieve Ethical Scenario
            ethical_scenario = self.get_scenario(scenario)

            if not ethical_scenario:
                logger.warning(f"[EVALUATION] Scenario not found: {scenario}")
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
        except Exception as e:
            logger.error(f"[EVALUATION ERROR] {e}", exc_info=True)
            return {"error": "An error occurred during evaluation."}

    def get_scenario(self, scenario_text: str) -> Dict:
        """
        Retrieve predefined ethical scenarios from the database or built-in list.

        :param scenario_text: The text of the scenario to look up.
        :return: Dictionary with scenario details or None if not found.
        """
        try:
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
            logger.debug(f"[SCENARIO FALLBACK] Using predefined scenario for: {scenario_text}")
            return predefined_scenarios.get(scenario_text)
        except Exception as e:
            logger.error(f"[SCENARIO RETRIEVAL ERROR] {e}", exc_info=True)
            return None

    def store_ethics_memory(self, decision: Dict[str, Any]):
        """
        Store ethical decisions in the memory database.

        :param decision: Dictionary containing details of the ethical decision.
        """
        try:
            query = """
            CREATE (e:Ethics {scenario: $scenario, choice: $choice, outcome: $outcome, lesson: $lesson})
            """
            self.db.run_query(query, decision)
            logger.info(f"[MEMORY STORED] Ethical decision stored: {decision}")
        except Exception as e:
            logger.error(f"[MEMORY STORAGE ERROR] {e}", exc_info=True)