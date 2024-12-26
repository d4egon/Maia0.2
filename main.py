import os
import sys
import logging
import magic
import time
from functools import lru_cache
from flask import Flask, render_template, request, jsonify
from werkzeug.utils import secure_filename
from dotenv import load_dotenv
from config.settings import CONFIG
from core.neo4j_connector import Neo4jConnector
from core.memory_engine import MemoryEngine
from core.file_parser import FileParser
from NLP.response_generator import ResponseGenerator
from NLP.nlp_engine import NLP
from core.emotion_engine import EmotionEngine
from core.emotion_fusion_engine import EmotionFusionEngine
from core.conversation_engine import ConversationEngine
from core.dream_engine import DreamEngine
from core.ethics_engine import EthicsEngine
from core.memory_linker import MemoryLinker
from core.context_search import ContextSearchEngine
from core.deduplication_engine import DeduplicationEngine
from NLP.consciousness_engine import ConsciousnessEngine
from NLP.intent_detector import IntentDetector
from core.self_initiated_conversation import SelfInitiatedConversation

# Load Environment Variables
load_dotenv()

# Configure Logging
logging.basicConfig(
    level=logging.INFO if os.getenv("FLASK_DEBUG", "false").lower() != "true" else logging.DEBUG,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler("main.log"),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

# Constants
UPLOAD_FOLDER = os.getenv("UPLOAD_FOLDER", os.path.join(os.getcwd(), "uploads"))
MAX_FILE_SIZE_MB = int(os.getenv("MAX_FILE_SIZE_MB", 100))
ALLOWED_EXTENSIONS = {'txt', 'pdf', 'docx', 'jpg', 'png', 'jpeg'}

# Flask App Initialization
app = Flask(
    __name__,
    template_folder=os.path.join(os.getcwd(), "web_server", "templates"),
    static_folder=os.path.join(os.getcwd(), "web_server", "static"),
)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = MAX_FILE_SIZE_MB * 1024 * 1024  # Convert MB to bytes

# Secure Headers Setup
@app.after_request
def apply_csp_headers(response):
    response.headers['Content-Security-Policy'] = (
        "default-src 'self'; script-src 'self'; style-src 'self' 'unsafe-inline'; "
        "font-src 'self'; img-src 'self' data:; connect-src 'self' ws: wss:"
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
    neo4j_uri = CONFIG.get("NEO4J_URI")
    neo4j_user = CONFIG.get("NEO4J_USER")
    neo4j_password = CONFIG.get("NEO4J_PASSWORD")

    neo4j = Neo4jConnector(neo4j_uri, neo4j_user, neo4j_password)
    memory_engine = MemoryEngine(neo4j)
    response_gen = ResponseGenerator(memory_engine, neo4j)
    file_parser = FileParser()
    nlp_engine = NLP(memory_engine, response_gen, neo4j)
    emotion_engine = EmotionEngine()
    emotion_fusion_engine = EmotionFusionEngine(memory_engine, nlp_engine)
    dream_engine = DreamEngine(memory_engine, ContextSearchEngine(neo4j))
    ethics_engine = EthicsEngine(neo4j)
    memory_linker = MemoryLinker(neo4j)
    context_search_engine = ContextSearchEngine(neo4j)
    deduplication_engine = DeduplicationEngine(neo4j_uri, neo4j_user, neo4j_password)
    consciousness_engine = ConsciousnessEngine(memory_engine, emotion_engine)
    intent_detector = IntentDetector()

    conversation_engine = ConversationEngine(
        memory_engine,
        response_gen,
        None,
        context_search_engine
    )
    self_initiated_conversation = SelfInitiatedConversation(memory_engine, conversation_engine, None)

    logger.info("[INIT SUCCESS] All services initialized successfully.")
except Exception as e:
    logger.critical(f"[INIT FAILED] Failed to initialize services: {e}", exc_info=True)
    sys.exit(1)

# Cache for Gallery Images
gallery_cache = {}

@lru_cache(maxsize=100)
def cached_get_gallery_images():
    logger.info("[GALLERY] Fetching gallery images.")
    image_folder = os.path.join(app.static_folder, "images")
    all_files = os.listdir(image_folder)
    image_files = [f for f in all_files if f.endswith(('.png', '.jpg', '.jpeg', '.webp'))]
    logger.debug(f"[GALLERY] Found images: {image_files}")
    return list(set(image_files))

# Utility Functions
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def get_file_size(filepath):
    size = os.path.getsize(filepath) / (1024 * 1024)
    logger.debug(f"[FILE SIZE] File: {filepath} | Size: {size:.2f} MB")
    return size

def clean_file(filepath):
    if os.path.exists(filepath):
        os.remove(filepath)
        logger.info(f"[CLEANUP] Removed file '{filepath}'.")

# Routes
@app.route('/')
def index():
    logger.info("[ROUTE] Index accessed.")
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({"message": "No file uploaded", "status": "error"}), 400

    file = request.files['file']
    if not file.filename:
        return jsonify({"message": "Empty file name", "status": "error"}), 400

    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)

        mime = magic.from_file(filepath, mime=True)
        if not mime.startswith(('text/', 'application/pdf', 'image/')):
            clean_file(filepath)
            return jsonify({"message": "Invalid file type", "status": "error"}), 400

        if get_file_size(filepath) > MAX_FILE_SIZE_MB:
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
            return jsonify({"message": "File processed successfully.", "status": "success"}), 200
        except Exception as e:
            clean_file(filepath)
            logger.error(f"[UPLOAD ERROR] Failed to process file: {e}", exc_info=True)
            return jsonify({"message": "Error processing file.", "status": "error"}), 500
    else:
        return jsonify({"message": "File type not allowed", "status": "error"}), 400

@app.route('/get_gallery_images', methods=['GET'])
def get_gallery_images():
    if 'gallery' not in gallery_cache or 'last_update' not in gallery_cache or (time.time() - gallery_cache['last_update']) > 3600:
        gallery_cache['gallery'] = {
            'images': cached_get_gallery_images(),
            'last_update': time.time()
        }
    return jsonify({"images": gallery_cache['gallery']['images']})

@app.route('/query_memory', methods=['GET'])
def query_memory():
    logger.info("[MEMORY QUERY] Querying latest memories.")
    try:
        page = request.args.get('page', 1, type=int)
        limit = request.args.get('limit', 5, type=int)
        offset = (page - 1) * limit
        query = """
        MATCH (m:Memory)
        RETURN m.text AS memory, m.last_updated AS lastUpdated
        ORDER BY m.last_updated DESC
        SKIP $offset LIMIT $limit
        """
        results = neo4j.run_query(query, {"offset": offset, "limit": limit})
        logger.debug(f"[MEMORY QUERY] Results: {results}")
        return jsonify({"results": results, "status": "success", "page": page, "limit": limit}), 200
    except Exception as e:
        logger.error(f"[MEMORY QUERY ERROR] {e}", exc_info=True)
        return jsonify({"message": "Failed to query memory.", "status": "error"}), 500

@app.route('/ask_maia', methods=['POST'])
def ask_maia():
    try:
        data = request.get_json()
        logger.info(f"[ASK MAIA] Received question: {data}")

        if not data or 'question' not in data:
            logger.error("[ASK MAIA] Invalid input.")
            return jsonify({"message": "Invalid input.", "status": "error"}), 400

        question = data['question']
        intent = nlp_engine.detect_intent(question)
        response, _ = nlp_engine.process(question)
        
        logger.info(f"[ASK MAIA] Response generated: {response}")
        return jsonify({"response": response, "intent": intent, "status": "success"}), 200
    except Exception as e:
        logger.error(f"[ASK MAIA] Error: {e}", exc_info=True)
        return jsonify({"message": "An error occurred.", "status": "error"}), 500

@app.route('/generate_dream', methods=['GET'])
def generate_dream():
    try:
        dream = dream_engine.generate_dream()
        logger.info(f"[DREAM GENERATED] {dream[:100]}{'...' if len(dream) > 100 else ''}")
        return jsonify({"dream": dream, "status": "success"}), 200
    except Exception as e:
        logger.error(f"[DREAM GENERATION ERROR] {e}", exc_info=True)
        return jsonify({"message": "Failed to generate dream.", "status": "error"}), 500

@app.route('/evaluate_ethics', methods=['POST'])
def evaluate_ethics():
    try:
        data = request.get_json()
        if not data or 'scenario' not in data or 'choice' not in data:
            return jsonify({"message": "Invalid data provided.", "status": "error"}), 400

        scenario = data['scenario']
        choice = data['choice']
        result = ethics_engine.evaluate_decision(scenario, choice)
        return jsonify({"result": result, "status": "success"}), 200
    except Exception as e:
        logger.error(f"[ETHICS EVALUATION ERROR] {e}", exc_info=True)
        return jsonify({"message": "Failed to evaluate ethical decision.", "status": "error"}), 500

@app.route('/introspect', methods=['GET'])
def introspect():
    try:
        introspection = consciousness_engine.introspect()
        logger.info(f"[INTROSPECTION] {introspection[:100]}{'...' if len(introspection) > 100 else ''}")
        return jsonify({"introspection": introspection, "status": "success"}), 200
    except Exception as e:
        logger.error(f"[INTROSPECTION ERROR] {e}", exc_info=True)
        return jsonify({"message": "Failed to introspect.", "status": "error"}), 500

if __name__ == '__main__':
    logger.info("[START] MAIA Server is starting...")
    self_initiated_conversation.start_scheduler()
    app.run(host='0.0.0.0', port=5000, debug=os.getenv("FLASK_DEBUG", "false").lower() == "true")
