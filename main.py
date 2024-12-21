import os
import sys
import logging

# Initialize Logging
logging.basicConfig(
    level=logging.DEBUG,  # Set to DEBUG for detailed logs
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler("maia_server.log"),  # Log to a file
        logging.StreamHandler(sys.stdout)       # Log to console
    ]
)
logger = logging.getLogger(__name__)

# Add the project root directory to the Python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Core Module Imports
from config.settings import CONFIG
from core.neo4j_connector import Neo4jConnector
from core.memory_engine import MemoryEngine
from core.file_parser import FileParser
from NLP.response_generator import ResponseGenerator
from flask import Flask, render_template, request, jsonify
from werkzeug.utils import secure_filename
from dotenv import load_dotenv

# Load Environment Variables
load_dotenv()

# Debug: Print Environment Variables
logger.debug(f"UPLOAD_FOLDER: {os.getenv('UPLOAD_FOLDER')}")
logger.debug(f"MAX_FILE_SIZE_MB: {os.getenv('MAX_FILE_SIZE_MB')}")
logger.debug(f"NEO4J_URI: {os.getenv('NEO4J_URI')}")
logger.debug(f"NEO4J_USER: {os.getenv('NEO4J_USER')}")
# Debugging environment variables
print("NEO4J_URI:", os.getenv("NEO4J_URI"))
print("NEO4J_USER:", os.getenv("NEO4J_USER"))
print("NEO4J_PASSWORD:", os.getenv("NEO4J_PASSWORD"))


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

# Secure Headers Setup
@app.after_request
def apply_csp_headers(response):
    """Apply Content Security Policy headers."""
    logger.debug("[CSP] Applying Content Security Policy headers.")
    response.headers['Content-Security-Policy'] = (
        "default-src 'self'; "
        "script-src 'self'; "
        "style-src 'self' 'unsafe-inline'; "
        "font-src 'self'; "
        "img-src 'self' data:; "
    )
    return response

# Ensure Upload Folder Exists
try:
    os.makedirs(UPLOAD_FOLDER, exist_ok=True)
    logger.info(f"[INIT] Upload folder ensured at: {UPLOAD_FOLDER}")
except Exception as e:
    logger.critical(f"[INIT ERROR] Failed to create upload folder: {e}", exc_info=True)
    sys.exit(1)

# Initialize Core Services
try:
    # Load Neo4j credentials
    neo4j_uri = CONFIG.get("NEO4J_URI")
    neo4j_user = CONFIG.get("NEO4J_USER")
    neo4j_password = CONFIG.get("NEO4J_PASSWORD")

    logger.info(f"[DEBUG] Neo4j URI: {neo4j_uri}")
    logger.info(f"[DEBUG] Neo4j User: {neo4j_user}")

    # Initialize Neo4j Connector
    logger.info("[INIT] Connecting to Neo4j...")
    neo4j = Neo4jConnector(neo4j_uri, neo4j_user, neo4j_password)

    # Initialize other services
    memory_engine = MemoryEngine(neo4j)
    response_gen = ResponseGenerator(memory_engine, neo4j)
    file_parser = FileParser()

    logger.info("[INIT SUCCESS] All services initialized successfully.")
except Exception as e:
    logger.critical(f"[INIT FAILED] Failed to initialize services: {e}", exc_info=True)
    sys.exit(1)

# Utility Functions
def get_file_size(filepath):
    """Get the file size in MB."""
    size = os.path.getsize(filepath) / (1024 * 1024)
    logger.debug(f"[FILE SIZE] File: {filepath} | Size: {size:.2f} MB")
    return size

def clean_file(filepath):
    """Remove uploaded file if it exists."""
    if os.path.exists(filepath):
        os.remove(filepath)
        logger.info(f"[CLEANUP] Removed file '{filepath}'.")

# Routes
@app.route('/')
def index():
    """Render the main page."""
    logger.info("[ROUTE] Index accessed.")
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    """Handle file uploads."""
    logger.info("[UPLOAD] File upload initiated.")
    if 'file' not in request.files:
        logger.warning("[UPLOAD ERROR] No file part in request.")
        return jsonify({"message": "No file uploaded", "status": "error"}), 400

    file = request.files['file']
    if not file.filename:
        logger.warning("[UPLOAD ERROR] Empty file name.")
        return jsonify({"message": "Empty file name", "status": "error"}), 400

    filename = secure_filename(file.filename)
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    file.save(filepath)
    logger.info(f"[UPLOAD] File saved: {filename}")

    if get_file_size(filepath) > MAX_FILE_SIZE_MB:
        logger.warning(f"[UPLOAD ERROR] File '{filename}' exceeds size limit.")
        clean_file(filepath)
        return jsonify({"message": "File too large", "status": "error"}), 413

    try:
        result = file_parser.parse(filepath)
        memory_engine.store_memory(
            text=result,
            emotions=["neutral"],
            extra_properties={"source": filename, "type": "file_upload"}
        )
        clean_file(filepath)
        logger.info(f"[UPLOAD SUCCESS] File '{filename}' processed successfully.")
        return jsonify({"message": "File processed and stored successfully.", "status": "success"}), 200

    except Exception as e:
        clean_file(filepath)
        logger.error(f"[UPLOAD ERROR] Failed to process file '{filename}': {e}", exc_info=True)
        return jsonify({"message": f"Error processing file: {str(e)}", "status": "error"}), 500

@app.route('/get_gallery_images', methods=['GET'])
def get_gallery_images():
    """Fetch gallery images."""
    logger.info("[GALLERY] Fetching gallery images.")
    image_folder = os.path.join(app.static_folder, "images")
    try:
        all_files = os.listdir(image_folder)
        image_files = [f for f in all_files if f.endswith(('.png', '.jpg', '.jpeg', '.webp'))]
        logger.debug(f"[GALLERY] Found images: {image_files}")
        return jsonify({"images": list(set(image_files))})  # Deduplicated
    except FileNotFoundError as e:
        logger.error(f"[GALLERY ERROR] Image folder not found: {e}")
        return jsonify({"message": "Error loading gallery.", "status": "error"}), 500
    except Exception as e:
        logger.error(f"[GALLERY ERROR] Unexpected error: {e}", exc_info=True)
        return jsonify({"message": "Unexpected error loading gallery.", "status": "error"}), 500

@app.route('/query_memory', methods=['GET'])
def query_memory():
    """Query the latest memories from Neo4j."""
    logger.info("[MEMORY QUERY] Querying latest memories.")
    try:
        query = """
        MATCH (m:Memory)
        RETURN m.text AS memory, m.last_updated AS lastUpdated
        ORDER BY m.last_updated DESC
        LIMIT 5
        """
        results = neo4j.run_query(query)
        logger.debug(f"[MEMORY QUERY] Results: {results}")
        return jsonify({"results": results, "status": "success"}), 200
    except Exception as e:
        logger.error(f"[MEMORY QUERY ERROR] {e}", exc_info=True)
        return jsonify({"message": f"Error querying memory: {str(e)}", "status": "error"}), 500

@app.route('/ask_maia', methods=['POST'])
def ask_maia():
    try:
        data = request.get_json()
        logger.info(f"[ASK MAIA] Received question: {data}")

        if not data or 'question' not in data:
            logger.error("[ASK MAIA] Invalid input.")
            return jsonify({"message": "Invalid input.", "status": "error"}), 400

        question = data['question']

        # Generate response using response_gen
        memory_data = {"text": question, "emotions": ["neutral"]}
        response = response_gen.generate_response(memory_data)

        logger.info(f"[ASK MAIA] Response generated: {response}")
        return jsonify({"response": response, "status": "success"}), 200

    except Exception as e:
        logger.error(f"[ASK MAIA] Error: {e}", exc_info=True)
        return jsonify({"message": "An error occurred.", "status": "error"}), 500


if __name__ == '__main__':
    logger.info("[START] MAIA Server is starting...")
    app.run(host='0.0.0.0', port=5000, debug=os.getenv("FLASK_DEBUG", "false").lower() == "true")
