# /web_server/brain_api.py

import os
from flask import Flask, request, jsonify
from core.brain_interface import BrainInterface
from core.signal_emulation import SignalPropagation
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

NEO4J_URI = os.getenv("NEO4J_URI")
NEO4J_USER = os.getenv("NEO4J_USER")
NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD")

# Initialize Flask app
app = Flask(__name__)

# Configure Neo4j using environment variables
brain = BrainInterface(
    uri=NEO4J_URI,
    user=NEO4J_USER,
    password=NEO4J_PASSWORD
)

signal_propagation = SignalPropagation(brain)

@app.route('/node', methods=['POST'])
def create_node():
    data = request.json
    node = brain.create_node(data['type'], data['name'], data.get('properties'))
    return jsonify(node)

@app.route('/relationship', methods=['POST'])
def create_relationship():
    data = request.json
    relationship = brain.create_relationship(
        data['source'], data['target'], data['type'], data.get('properties')
    )
    return jsonify(relationship)

@app.route('/signal', methods=['POST'])
def send_signal():
    data = request.json
    paths = signal_propagation.send_signal(data['start'], data.get('max_hops', 5))
    return jsonify(paths)

if __name__ == '__main__':
    app.run(debug=True)
