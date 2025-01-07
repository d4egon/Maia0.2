import os
import sys
import logging
import time
from threading import Thread
from functools import lru_cache
from tempfile import NamedTemporaryFile
from flask import Flask, render_template, request, jsonify, abort
from werkzeug.utils import secure_filename
from dotenv import load_dotenv  # type: ignore
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
from flask_socketio import SocketIO  # type: ignore
from sentence_transformers import SentenceTransformer # type: ignore

# Load Environment Variables
load_dotenv()

logging.basicConfig(
    level=logging.INFO if os.getenv("FLASK_DEBUG", "false").lower() != "true" else logging.DEBUG,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler("main.log"),
    ],
    stream=sys.stdout
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

socketio = SocketIO(app)
model = SentenceTransformer('fine_tuned_all_mpnet_base_v2')  # Correct initialization

# Secure Headers Setup
@app.after_request
def apply_csp_headers(response):
    response.headers['Content-Security-Policy'] = (
        "default-src 'self'; script-src 'self'; style-src 'self' 'unsafe-inline'; "
        "font-src 'self'; img-src 'self' data:; connect-src 'self' ws: wss:"
    )
    response.headers['X-Content-Type-Options'] = 'nosniff'
    response.headers['X-Frame-Options'] = 'SAMEORIGIN'  # Prevent clickjacking
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

    if not neo4j_uri or not neo4j_user or not neo4j_password:
        logger.critical("Missing Neo4j configuration. Check your .env file.")
        sys.exit(1)

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
    intent_detector = IntentDetector(memory_engine)

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

def validate_request_data(data, required_keys):
    if not data:
        abort(400, description="Invalid input data.")
    for key in required_keys:
        if key not in data or not isinstance(data[key], str) or not data[key].strip():
            abort(400, description=f"Invalid or missing key: {key}")

# Routes
@app.route('/')
def index():
    logger.info("[ROUTE] Index accessed.")
    return render_template('index.html')

@app.route('/embed', methods=['POST'])
def embed():
    data = request.json
    text = data.get('text')
    if not text:
        return jsonify({'error': 'No text provided'}), 400
    embedding = model.encode(text).tolist()
    
    # Continuous learning: Optionally update model here with new text
    # This would typically be done in a separate background process
    # model.train_on_new_data(text)     embedding = model.encode(text).tolist()
    
    # Continuous learning: Optionally update model here with new text
    # This would typically be done in a separate background process or thread
    try:
        update_model_with_text(text)
        logger.info(f"[MODEL UPDATE] Model updated with new text: {text[:50]}...")  # Log first 50 chars for brevity
    except Exception as e:
        logger.error(f"[MODEL UPDATE ERROR] {e}", exc_info=True)
    
    return jsonify({'embedding': embedding})

def update_model_with_text(text):
    # This function would ideally run in the background or on a separate thread
    # Here's a pseudo implementation:
    from threading import Thread
    def train_task(text):
        # Prepare data for training
        # This is a very basic example; in reality, you'd need more data pre-processing
        tokenized_input = model.tokenize(text)
        input_ids = tokenized_input["input_ids"]
        # Assuming you have some way to get labels or use the text in pairs
        # model.train_on_new_data(input_ids, label)  # Needs implementation
        logger.info(f"[MODEL TRAIN] Training on text: {text[:50]}...")  # Log first 50 chars for brevity

    Thread(target=train_task, args=(text,)).start()

@app.route('/upload', methods=['POST'])
def upload_file():
    """
    Handle file uploads with optional advanced processing.
    """
    if 'file' not in request.files:
        return jsonify({"message": "No file uploaded", "status": "error"}), 400

    file = request.files['file']
    if not file.filename or not allowed_file(file.filename):
        return jsonify({"message": "Invalid file type", "status": "error"}), 400

    filename = secure_filename(file.filename)
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)

    try:
        # Save the file temporarily
        file.save(filepath)

        # Parse the file
        result = file_parser.parse(filepath)
        if not result.strip():
            raise ValueError("File content could not be processed or is empty.")

        # Advanced processing (e.g., metadata extraction) based on request parameter
        is_advanced = request.args.get("advanced", "false").lower() == "true"
        if is_advanced:
            logger.info("[ADVANCED PROCESSING] Additional processing steps applied.")
            # Add advanced-specific logic here (e.g., semantic analysis, metadata extraction)

        # Store the parsed content in memory
        memory_engine.store_memory(
            text=result,
            emotions=["neutral"],  # Placeholder emotion
            extra_properties={"source": filename, "type": "advanced_upload" if is_advanced else "upload"}
        )

        # Continuous Learning: Train model on new file content
        train_model_on_file_content(result)

        # Clean up the temporary file
        os.remove(filepath)

        logger.info(f"[UPLOAD SUCCESS] File '{filename}' processed and stored successfully.")
        return jsonify({"message": "File processed successfully.", "status": "success"}), 200
    except ValueError as ve:
        os.remove(filepath)
        logger.warning(f"[UPLOAD WARNING] {ve}")
        return jsonify({"message": str(ve), "status": "warning"}), 400
    except Exception as e:
        os.remove(filepath)
        logger.error(f"[UPLOAD ERROR] {e}", exc_info=True)
        return jsonify({"message": "An error occurred during processing.", "status": "error"}), 500

def train_model_on_file_content(content):
    # This would be more complex in practice, involving data preparation and batching
    sentences = content.split('. ')
    for sentence in sentences:
        update_model_with_text(sentence)  # Use our earlier function for individual sentences

@app.route('/ask_maia', methods=['POST'])
def ask_maia():
    try:
        data = request.get_json()
        validate_request_data(data, ['question'])

        question = data['question']
        intent = nlp_engine.detect_intent(question)
        response, _ = nlp_engine.process(question)

        # Log the interaction for potential future learning
        memory_engine.store_memory(text=f"Q: {question}\nA: {response}", emotions=["neutral"], extra_properties={"type": "conversation"})

        return jsonify({"response": response, "intent": intent, "status": "success"}), 200
    except Exception as e:
        logger.error(f"[ASK MAIA] Error: {e}", exc_info=True)
        return jsonify({"message": "An error occurred.", "status": "error"}), 500

@app.route('/get_gallery_images', methods=['GET'])
def get_gallery_images():
    if 'gallery' not in gallery_cache or 'last_update' not in gallery_cache or (time.time() - gallery_cache['last_update']) > 3600:
        gallery_cache['gallery'] = {
            'images': cached_get_gallery_images(),
            'last_update': time.time()
        }
    return jsonify({"images": gallery_cache['gallery']['images']})

if __name__ == "__main__":
    logger.info("[START] MAIA Server is starting...")
    self_initiated_conversation.start_scheduler()
    socketio.run(app, host="0.0.0.0", port=5000, debug=os.getenv("FLASK_DEBUG", "false").lower() == "true")