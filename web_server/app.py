from flask import Flask, request, jsonify
from werkzeug.utils import secure_filename
from file_parser import FileParser
from core.neo4j_connector import Neo4jConnector
from core.memory_engine import MemoryEngine
from NLP.response_generator import ResponseGenerator

UPLOAD_FOLDER = "uploads"
MAX_FILE_SIZE_MB = 100

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Initialize Core Services
neo4j = Neo4jConnector("neo4j+s://46dc0ffd.databases.neo4j.io:7687", "neo4j", "YOUR_PASSWORD")
memory_engine = MemoryEngine(neo4j)
response_gen = ResponseGenerator(memory_engine, neo4j)
file_parser = FileParser()

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({"error": "No file uploaded"}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "Empty file"}), 400

    # Save uploaded file securely
    filename = secure_filename(file.filename)
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    file.save(filepath)

    # Check file size
    filesize = os.path.getsize(filepath)
    if (filesize / (1024 * 1024)) > MAX_FILE_SIZE_MB:
        os.remove(filepath)
        return jsonify({"error": "File too large"}), 413

    # Process File
    result = file_parser.parse_file(filepath)
    os.remove(filepath)  # Cleanup after processing
    return jsonify(result), 200

if __name__ == '__main__':
    if not os.path.exists(UPLOAD_FOLDER):
        os.makedirs(UPLOAD_FOLDER)
    app.run(debug=True)