# File: /core/feedback_loops.py

import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class FeedbackLoops:
    def __init__(self, graph_client):
        """
        Initialize FeedbackLoops with a graph client for database operations.

        :param graph_client: An instance of a class that can run Cypher queries.
        """
        self.graph_client = graph_client

    def prompt_user_validation(self, node_id, name, attributes):
        """
        Prompt the user to validate or correct node attributes in the graph database.

        :param node_id: The ID of the node in the graph.
        :param name: The name of the node for display purposes.
        :param attributes: Dictionary of current attributes for the node.
        :return: None, updates node attributes in the database if necessary.
        """
        logger.info(f"Prompting validation for node '{name}' with ID: {node_id}")
        
        print(f"Validate the attributes of '{name}':")
        for key, value in attributes.items():
            print(f"- {key}: {value}")

        while True:
            valid = input("Is this correct? (yes/no): ").strip().lower()
            if valid not in ('yes', 'no'):
                print("Please answer 'yes' or 'no'.")
                continue
            break

        if valid == "no":
            updated_attributes = self._get_updated_attributes()
            if updated_attributes:
                self._update_node_attributes(node_id, updated_attributes)

    def _get_updated_attributes(self):
        """
        Collect updated attributes from user input.

        :return: Dictionary of updated attributes or None if input is invalid.
        """
        while True:
            raw_input = input("Enter correct attributes (key=value pairs separated by commas): ").strip()
            if not raw_input:
                logger.warning("No attributes provided for update.")
                return None

            try:
                attributes = {}
                for pair in raw_input.split(','):
                    key, value = pair.split('=')
                    attributes[key.strip()] = value.strip()
                return attributes
            except ValueError:
                print("Please ensure all attributes are in 'key=value' format.")

    def _update_node_attributes(self, node_id, attributes):
        """
        Update node attributes in the graph database.

        :param node_id: The ID of the node to update.
        :param attributes: Dictionary of attributes to update.
        :raises Exception: If there's an error updating the node in the database.
        """
        try:
            set_clause = ", ".join([f"n.{key} = '{value}'" for key, value in attributes.items()])
            query = f"""
            MATCH (n)
            WHERE n.id = '{node_id}'
            SET {set_clause}
            """
            self.graph_client.run_query(query)
            logger.info(f"Updated node attributes for node with ID: {node_id}")
        except Exception as e:
            logger.error(f"Failed to update node attributes: {e}")
            raise