# File: /core/interactive_learning.py

import logging
from typing import List, Dict

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class InteractiveLearning:
    def __init__(self, graph_client):
        """
        Initialize InteractiveLearning with a graph client for database operations.

        :param graph_client: An instance of a class that can run Cypher queries.
        """
        self.graph_client = graph_client

    def identify_knowledge_gaps(self) -> List[Dict]:
        """
        Identify nodes (emotions) that lack an example context.

        :return: List of dictionaries containing ID and name of nodes with missing example contexts.
        """
        query = """
        MATCH (n:Emotion)
        WHERE NOT EXISTS(n.example_context)
        RETURN n.id AS id, n.name AS name
        """
        try:
            result = self.graph_client.run_query(query)
            logger.info(f"Identified {len(result)} knowledge gaps.")
            return result
        except Exception as e:
            logger.error(f"Error identifying knowledge gaps: {e}")
            raise

    def ask_questions(self, knowledge_gaps: List[Dict]):
        """
        Interactively ask for and update missing example contexts for given knowledge gaps.

        :param knowledge_gaps: List of dictionaries containing 'id' and 'name' of nodes needing context.
        """
        for gap in knowledge_gaps:
            try:
                logger.info(f"Querying user for example context for emotion: {gap['name']}")
                print(f"Help me understand '{gap['name']}' better!")
                example_context = self._get_valid_input(f"Can you give me an example of {gap['name']}? ")
                
                if example_context:
                    self._update_example_context(gap['id'], example_context)
                else:
                    logger.warning(f"No example context provided for {gap['name']}")
            except Exception as e:
                logger.error(f"Error asking questions for {gap['name']}: {e}")

    def _get_valid_input(self, prompt: str) -> str:
        """
        Get valid input from the user, ensuring it's not empty.

        :param prompt: The question or prompt to display to the user.
        :return: The user's input as a string.
        """
        while True:
            user_input = input(prompt).strip()
            if user_input:
                return user_input
            print("Please provide a non-empty response.")

    def _update_example_context(self, node_id: str, example_context: str):
        """
        Update the example context for a node in the database.

        :param node_id: The ID of the node to update.
        :param example_context: The example context to set for the node.
        """
        query = f"""
        MATCH (n:Emotion {{id: '{node_id}'}})
        SET n.example_context = '{example_context.replace("'", "''")}'
        """
        try:
            self.graph_client.run_query(query)
            logger.info(f"Updated example context for node ID: {node_id}")
        except Exception as e:
            logger.error(f"Failed to update example context for node ID {node_id}: {e}")
            raise