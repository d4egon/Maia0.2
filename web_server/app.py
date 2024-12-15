# Filename: /web_server/app.py

import os
import logging
from flask import Flask, request, jsonify, render_template
from werkzeug.utils import secure_filename

# Core System Imports
from config.settings import CONFIG
from core.neo4j_connector import Neo4jConnector
from core.memory_engine import MemoryEngine
from core.file_parser import FileParser
from core.response_generator import ResponseGenerator

# Initialize Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Constants
UPLOAD_FOLDER = "uploads"
MAX_FILE_SIZE_MB = 100

# Flask App Initialization
app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Initialize Core Services
try:
    neo4j = Neo4jConnector(
        CONFIG["NEO4J_URI"],
        CONFIG["NEO4J_USER"],
        CONFIG["NEO4J_PASSWORD"]
    )
    memory_engine = MemoryEngine(neo4j)
    response_gen = ResponseGenerator(memory_engine, neo4j)
    file_parser = FileParser()
    logger.info("[INIT] Services initialized successfully.")
except Exception as e:
    logger.error(f"[INIT FAILED] Service initialization error: {e}", exc_info=True)


# Utility to get file size in MB
def get_file_size(filepath):
    return os.path.getsize(filepath) / (1024 * 1024)


# Routes
@app.route('/')
def index():
    """Render the main upload page."""
    return render_template('index.html')


@app.route('/upload', methods=['POST'])
def upload_file():
    """Handle file uploads."""
    if 'file' not in request.files:
        logger.error("[UPLOAD FAILED] No file uploaded.")
        return jsonify({"message": "No file uploaded", "status": "error"}), 400

    file = request.files['file']
    if file.filename == '':
        logger.error("[UPLOAD FAILED] Empty file name.")
        return jsonify({"message": "Empty file name", "status": "error"}), 400

    # Save the file securely
    filename = secure_filename(file.filename)
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    file.save(filepath)

    # Check file size
    if get_file_size(filepath) > MAX_FILE_SIZE_MB:
        os.remove(filepath)
        logger.error("[UPLOAD FAILED] File too large.")
        return jsonify({"message": "File too large", "status": "error"}), 413

    try:
        # Process the file
        result = file_parser.parse(filepath)

        # Store the result in MAIA's memory
        memory_engine.store_memory(
            text=result,
            emotion="neutral",
            additional_data={"source": filename, "type": "file_upload"}
        )

        os.remove(filepath)  # Cleanup after processing
        logger.info(f"[UPLOAD SUCCESS] File '{filename}' processed and stored.")
        return jsonify({"message": "File processed and stored successfully!", "status": "success"}), 200

    except Exception as e:
        os.remove(filepath)  # Cleanup on failure
        logger.error(f"[UPLOAD FAILED] Error processing file: {e}", exc_info=True)
        return jsonify({"message": f"Error processing file: {str(e)}", "status": "error"}), 500


@app.route('/query_memory', methods=['GET'])
def query_memory():
    """Query the latest memories stored in MAIA's database."""
    try:
        query = """
        MATCH (m:Memory)
        RETURN m.text AS memory, m.last_updated AS lastUpdated
        ORDER BY m.last_updated DESC
        LIMIT 5
        """
        results = neo4j.run_query(query)
        logger.info("[QUERY SUCCESS] Memory queried successfully.")
        return jsonify({"message": "Memory query successful", "results": results, "status": "success"}), 200
    except Exception as e:
        logger.error(f"[QUERY FAILED] Error querying memory: {e}", exc_info=True)
        return jsonify({"message": f"Error querying memory: {str(e)}", "status": "error"}), 500


@app.route('/ask_maia', methods=['POST'])
def ask_maia():
    """Ask MAIA a question about her memories."""
    data = request.get_json()
    if not data or 'question' not in data:
        logger.error("[ASK FAILED] No question provided.")
        return jsonify({"message": "No question provided", "status": "error"}), 400

    question = data['question']
    try:
        response = response_gen.generate_response(question)
        logger.info(f"[ASK SUCCESS] User: '{question}' | Response: '{response}'")
        return jsonify({"message": "Response generated successfully", "response": response, "status": "success"}), 200
    except Exception as e:
        logger.error(f"[ASK FAILED] Error generating response: {e}", exc_info=True)
        return jsonify({"message": f"Error generating response: {str(e)}", "status": "error"}), 500


# Ensure Upload Folder Exists
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)
    logger.info("[INIT] Upload folder created.")

if __name__ == '__main__':
    app.run(debug=True)