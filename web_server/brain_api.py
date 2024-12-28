# File: /web_server/brain_api.py
# Location: /web_server

import os
from flask import Flask, request, jsonify
from dotenv import load_dotenv
from flasgger import Swagger
from flask_talisman import Talisman
from flask_caching import Cache
import logging
from logging.handlers import RotatingFileHandler
from NLP.conciousness_engine import ConciousnessEngine
from NLP.nlp_engine import NLPEngine
from core.deduplication_engine import DeduplicationEngine
from core.attribute_enrichment import AttributeEnrichment
from core.interactive_learning import InteractiveLearning
from core.semantic_builder import SemanticBuilder
from core.feedback_loops import FeedbackLoops
from core.neo4j_connector import Neo4jConnector
from core.signal_emulation import SignalPropagation

# Load environment variables
load_dotenv()

# Retrieve credentials from .env
NEO4J_URI = os.getenv("NEO4J_URI")
NEO4J_USER = os.getenv("NEO4J_USER")
NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD")

app = Flask(__name__)

# Setup logging
handler = RotatingFileHandler('brain_api.log', maxBytes=10000, backupCount=1)
handler.setLevel(logging.INFO)
app.logger.addHandler(handler)

# Initialize Neo4j connection (consider lazy loading if not always needed)
neo4j_conn = Neo4jConnector(uri=NEO4J_URI, user=NEO4J_USER, password=NEO4J_PASSWORD)

# Flask extensions for security and performance
Talisman(app, content_security_policy=None)
cache = Cache(app, config={'CACHE_TYPE': 'simple'})

# Setup Swagger for API documentation
swagger = Swagger(app)

def get_deduplication_engine():
    if not hasattr(app, "deduplication_engine"):
        app.deduplication_engine = DeduplicationEngine(uri=NEO4J_URI, user=NEO4J_USER, password=NEO4J_PASSWORD)
    return app.deduplication_engine

def get_attribute_enrichment():
    if not hasattr(app, "attribute_enrichment"):
        app.attribute_enrichment = AttributeEnrichment(graph_client=neo4j_conn)
    return app.attribute_enrichment

def get_interactive_learning():
    if not hasattr(app, "interactive_learning"):
        app.interactive_learning = InteractiveLearning(graph_client=neo4j_conn)
    return app.interactive_learning

def get_semantic_builder():
    if not hasattr(app, "semantic_builder"):
        app.semantic_builder = SemanticBuilder(graph_client=neo4j_conn)
    return app.semantic_builder

def get_feedback_loops():
    if not hasattr(app, "feedback_loops"):
        app.feedback_loops = FeedbackLoops(graph_client=neo4j_conn)
    return app.feedback_loops

@app.route("/v1/deduplicate", methods=["POST"])
def deduplicate_v1():
    """
    Perform deduplication on graph nodes with a specific label.
    ---
    parameters:
      - name: label
        in: body
        type: string
        required: false
        default: Emotion
    responses:
      200:
        description: Deduplication completed
      500:
        description: An error occurred during deduplication
    """
    try:
        label = request.json.get("label", "Emotion")
        get_deduplication_engine().deduplicate(label)
        return jsonify({"message": f"Deduplication completed for label: {label}"}), 200
    except Exception as e:
        app.logger.error(f"Deduplication error: {str(e)}")
        return jsonify({"error": "An error occurred during deduplication", "details": str(e)}), 500

@app.route("/v1/enrich_attributes", methods=["POST"])
def enrich_attributes_v1():
    """
    Enrich attributes of nodes based on the label, either automatically or interactively.
    ---
    parameters:
      - name: label
        in: body
        type: string
        required: false
        default: Emotion
      - name: auto
        in: body
        type: boolean
        required: false
        default: true
    responses:
      200:
        description: Attributes enriched
      500:
        description: An error occurred during attribute enrichment
    """
    try:
        label = request.json.get("label", "Emotion")
        auto_mode = request.json.get("auto", True)
        enrichment = get_attribute_enrichment()
        missing_nodes = enrichment.get_missing_attributes(label)
        if auto_mode:
            for node in missing_nodes:
                enrichment.auto_enrichment(node["id"], node["name"])
        else:
            enrichment.interactive_enrichment(missing_nodes)
        return jsonify({"message": f"Attributes enriched for label: {label}"}), 200
    except Exception as e:
        app.logger.error(f"Attribute enrichment error: {str(e)}")
        return jsonify({"error": "An error occurred during attribute enrichment", "details": str(e)}), 500

@app.route("/v1/interactive_learning", methods=["POST"])
def interactive_learning_v1():
    """
    Initiate an interactive learning session to fill knowledge gaps.
    ---
    responses:
      200:
        description: Interactive learning session completed
      500:
        description: An error occurred during interactive learning
    """
    try:
        learning = get_interactive_learning()
        knowledge_gaps = learning.identify_knowledge_gaps()
        learning.ask_questions(knowledge_gaps)
        return jsonify({"message": "Interactive learning completed."}), 200
    except Exception as e:
        app.logger.error(f"Interactive learning error: {str(e)}")
        return jsonify({"error": "An error occurred during interactive learning", "details": str(e)}), 500

@app.route("/v1/recursive_introspection", methods=["POST"])
def recursive_introspection():
    """
    Perform recursive introspection based on a user-provided theme.
    ---
    parameters:
      - name: theme
        in: body
        type: string
        required: true
    responses:
      200:
        description: Introspection completed successfully
      500:
        description: An error occurred
    """
    try:
        theme = request.json.get("theme")
        results = consciousness_engine.expanded_recursive_reflection(theme, depth=5)
        logger.info(f"[RECURSIVE INTROSPECTION] Results: {results}")
        return jsonify({"results": results, "status": "success"}), 200
    except Exception as e:
        logger.error(f"[RECURSIVE INTROSPECTION ERROR] {e}", exc_info=True)
        return jsonify({"message": "Failed to perform introspection.", "status": "error"}), 500

@app.route("/v1/build_relationships", methods=["POST"])
def build_relationships_v1():
    """
    Build semantic relationships between nodes based on their descriptions.
    ---
    parameters:
      - name: label
        in: body
        type: string
        required: false
        default: Emotion
    responses:
      200:
        description: Relationships built
      500:
        description: An error occurred while building relationships
    """
    try:
        label = request.json.get("label", "Emotion")
        get_semantic_builder().build_relationships(label)
        return jsonify({"message": f"Relationships built for label: {label}"}), 200
    except Exception as e:
        app.logger.error(f"Relationship building error: {str(e)}")
        return jsonify({"error": "An error occurred while building relationships", "details": str(e)}), 500

@app.route("/v1/validate_feedback", methods=["POST"])
def validate_feedback_v1():
    """
    Validate feedback for node attributes in the graph.
    ---
    parameters:
      - name: node_id
        in: body
        type: string
        required: true
      - name: name
        in: body
        type: string
        required: true
      - name: attributes
        in: body
        type: object
        required: true
    responses:
      200:
        description: Feedback validation completed
      500:
        description: An error occurred during feedback validation
    """
    try:
        node_id = request.json["node_id"]
        name = request.json["name"]
        attributes = request.json["attributes"]
        get_feedback_loops().prompt_user_validation(node_id, name, attributes)
        return jsonify({"message": "Feedback validation completed."}), 200
    except Exception as e:
        app.logger.error(f"Feedback validation error: {str(e)}")
        return jsonify({"error": "An error occurred during feedback validation", "details": str(e)}), 500

@app.route("/v1/propagate_signal", methods=["POST"])
def propagate_signal_v1():
    """
    Propagate a signal through the graph from a starting node.
    ---
    parameters:
      - name: start_node
        in: body
        type: string
        required: true
      - name: max_hops
        in: body
        type: integer
        required: false
        default: 5
    responses:
      200:
        description: Signal propagation paths
      500:
        description: An error occurred during signal propagation
    """
    try:
        start_node = request.json["start_node"]
        max_hops = request.json.get("max_hops", 5)
        signal_propagation = SignalPropagation(neo4j_conn)
        paths = signal_propagation.send_signal(start_node, max_hops)
        return jsonify({"paths": [str(path) for path in paths]}), 200
    except Exception as e:
        app.logger.error(f"Signal propagation error: {str(e)}")
        return jsonify({"error": "An error occurred during signal propagation", "details": str(e)}), 500

@app.route("/v1/visualize_thoughts", methods=["GET"])
def visualize_thoughts():
    """
    Generate a real-time visualization of M.A.I.A.'s thought process.
    ---
    responses:
      200:
        description: Visualization generated successfully
      500:
        description: An error occurred
    """
    try:
        thought_graph = memory_linker.generate_visualization()
        logger.info(f"[THOUGHT VISUALIZATION] Generated successfully.")
        return jsonify({"visualization": thought_graph, "status": "success"}), 200
    except Exception as e:
        logger.error(f"[VISUALIZATION ERROR] {e}", exc_info=True)
        return jsonify({"message": "Failed to generate visualization.", "status": "error"}), 500


@app.errorhandler(Exception)
def handle_exception(e):
    app.logger.error(f"An error occurred: {str(e)}")
    return jsonify({"error": "An unexpected error occurred", "details": str(e)}), 500

@app.route("/v1/conversation", methods=["POST"])
def dynamic_conversation():
    """
    Start a dynamic conversation with M.A.I.A. based on user input.
    ---
    parameters:
      - name: input
        in: body
        type: string
        required: true
    responses:
      200:
        description: Conversation response
      500:
        description: An error occurred
    """
    try:
        user_input = request.json.get("input")
        logger.info(f"[CONVERSATION] User Input: {user_input}")
        intent = nlp_engine.detect_intent(user_input)
        response, _ = consciousness_engine.reflect(user_input)
        logger.info(f"[CONVERSATION RESPONSE] {response}")
        return jsonify({"response": response, "intent": intent, "status": "success"}), 200
    except Exception as e:
        logger.error(f"[CONVERSATION ERROR] {e}", exc_info=True)
        return jsonify({"message": "An error occurred during the conversation.", "status": "error"}), 500


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, ssl_context='adhoc')  # Use 'adhoc' for development, secure SSL in production