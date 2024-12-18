import os
import sys
import logging
from flask import Flask, render_template, request, jsonify
from werkzeug.utils import secure_filename
from dotenv import load_dotenv # type: ignore

# Add the project root directory to the Python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Core Module Imports
from config.settings import CONFIG
from core.neo4j_connector import Neo4jConnector
from core.memory_engine import MemoryEngine
from core.file_parser import FileParser
from NLP.response_generator import ResponseGenerator

# Load Environment Variables
load_dotenv()

# Initialize Logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

# Constants
UPLOAD_FOLDER = os.getenv("UPLOAD_FOLDER", os.path.join(os.getcwd(), "uploads"))
MAX_FILE_SIZE_MB = int(os.getenv("MAX_FILE_SIZE_MB", 100))

# Flask App Initialization
app = Flask(
    __name__,
    template_folder=os.path.join(os.getcwd(), "web_server", "templates"),
    static_folder=os.path.join(os.getcwd(), "web_server", "static"),
)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Initialize Core Services
try:
    # Load Neo4j credentials from the CONFIG
    neo4j_uri = CONFIG.get("NEO4J_URI")
    neo4j_user = CONFIG.get("NEO4J_USER")
    neo4j_password = CONFIG.get("NEO4J_PASSWORD")

    # Debugging print to ensure credentials are loaded
    logger.info(f"[DEBUG] Neo4j URI: {neo4j_uri}")
    logger.info(f"[DEBUG] Neo4j USER: {neo4j_user}")

    # Initialize Neo4j Connector
    logger.info("[INIT] Connecting to Neo4j AuraDB...")
    neo4j = Neo4jConnector(neo4j_uri, neo4j_user, neo4j_password)

    # Initialize remaining services
    memory_engine = MemoryEngine(neo4j)
    response_gen = ResponseGenerator(memory_engine, neo4j)
    file_parser = FileParser()

    logger.info("[INIT SUCCESS] Services initialized successfully.")
except Exception as e:
    logger.critical(f"[INIT FAILED] Failed to initialize Neo4j services: {e}", exc_info=True)
    sys.exit(1)

# Utility Functions
def get_file_size(filepath):
    """Get the file size in MB."""
    return os.path.getsize(filepath) / (1024 * 1024)

def clean_file(filepath):
    """Remove uploaded file if it exists."""
    if os.path.exists(filepath):
        os.remove(filepath)
        logger.info(f"[CLEANUP] Removed file '{filepath}'.")

# Routes
@app.route('/')
def index():
    """Render the main upload page."""
    logger.info("[ROUTE] Index route accessed.")
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    """Handle file uploads."""
    if 'file' not in request.files:
        return jsonify({"message": "No file uploaded", "status": "error"}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({"message": "Empty file name", "status": "error"}), 400

    filename = secure_filename(file.filename)
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    file.save(filepath)

    if get_file_size(filepath) > MAX_FILE_SIZE_MB:
        clean_file(filepath)
        return jsonify({"message": "File too large", "status": "error"}), 413

    try:
        result = file_parser.parse(filepath)
        memory_engine.store_memory(
            text=result,
            emotion="neutral",
            additional_data={"source": filename, "type": "file_upload"}
        )
        clean_file(filepath)
        logger.info(f"[UPLOAD] File '{filename}' processed successfully.")
        return jsonify({"message": "File processed and stored successfully!", "status": "success"}), 200

    except Exception as e:
        clean_file(filepath)
        logger.error(f"[UPLOAD ERROR] Failed to process file '{filename}': {e}", exc_info=True)
        return jsonify({"message": f"Error processing file: {str(e)}", "status": "error"}), 500

@app.route('/get_gallery_images', methods=['GET'])
def get_gallery_images():
    """Return a list of image filenames from the images directory."""
    images_folder = os.path.join(app.static_folder, 'images')
    valid_extensions = ('.png', '.webp', '.jpeg', '.jpg')

    try:
        images = [
            f for f in os.listdir(images_folder)
            if f.lower().endswith(valid_extensions)
        ]
        return jsonify({"images": images}), 200
    except Exception as e:
        return jsonify({"error": f"Failed to load images: {str(e)}"}), 500

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
        logger.info("[QUERY] Latest memories retrieved successfully.")
        return jsonify({"results": results, "status": "success"}), 200
    except Exception as e:
        logger.error(f"[QUERY ERROR] {e}", exc_info=True)
        return jsonify({"message": f"Error querying memory: {str(e)}", "status": "error"}), 500

@app.route('/ask_maia', methods=['POST'])
def ask_maia():
    """Ask MAIA a question about her memories."""
    data = request.get_json()
    if not data or 'question' not in data:
        return jsonify({"message": "No question provided", "status": "error"}), 400

    question = data['question']
    try:
        response = response_gen.generate("query", question)  # Corrected method
        logger.info(f"[ASK] Response generated for question: '{question}'")
        return jsonify({"response": response, "status": "success"}), 200
    except Exception as e:
        logger.error(f"[ASK ERROR] {e}", exc_info=True)
        return jsonify({"message": f"Error generating response: {str(e)}", "status": "error"}), 500

# Ensure Upload Folder Exists
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)
    logger.info(f"[INIT] Upload folder created at: {UPLOAD_FOLDER}")

if __name__ == '__main__':
    logger.info("[START] MAIA Server is starting...")
    debug_mode = os.getenv("FLASK_DEBUG", "false").lower() == "true"
    app.run(host='0.0.0.0', port=5000, debug=debug_mode)
