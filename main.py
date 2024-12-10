# main.py - Project Entry Point

import os
import time
import webbrowser
from subprocess import Popen
from flask import Flask, request, jsonify, render_template

# Backend Modules
from backend.emotion_engine import analyze_emotion
from backend.memory_persistence_engine import store_memory_in_neo4j, retrieve_memories_from_neo4j
from backend.ethics_engine import evaluate_ethics

# Initialize Flask App
app = Flask(__name__)

# --- Flask Routes ---

# Home Route
@app.route("/")
def home():
    return render_template("index.html")


# Store Memory Route
@app.route("/store_memory", methods=["POST"])
def store_memory():
    data = request.json
    event = data.get("event")
    content = data.get("content")
    emotion = data.get("emotion")
    intensity = data.get("intensity", 1)

    result = store_memory_in_neo4j(event, content, emotion, intensity)
    return jsonify({"message": "Memory stored!", "result": result})


# Retrieve Memories Route
@app.route("/retrieve_memories", methods=["GET"])
def retrieve_memories():
    emotion = request.args.get("emotion")
    memories = retrieve_memories_from_neo4j(emotion)
    return jsonify({"memories": memories})


# Chat Route
@app.route("/chat", methods=["POST"])
def chat():
    user_message = request.json.get("message", "")
    response = analyze_emotion(user_message)
    store_memory_in_neo4j("user_interaction", user_message, response["emotion"], response["intensity"])
    return jsonify({"reply": response["response_text"]})


# Analyze Route (Text + Image Analysis)
@app.route("/analyze", methods=["POST"])
def analyze():
    user_input = request.form.get("text", "").strip()
    image = request.files.get("image")
    activations, unknown_keywords = analyze_emotion(user_input, image)
    return jsonify({
        "activations": activations,
        "text_response": f"Analysis Complete! Emotional state: {activations}",
        "unknown_keywords": unknown_keywords,
    })


# Ethical Evaluation Route
@app.route("/ethics", methods=["POST"])
def ethics():
    scenario = request.json.get("scenario", "")
    decision = evaluate_ethics(scenario)
    return jsonify({"evaluation": decision})


# --- Auto-Start System ---
def start_services():
    try:
        # Start Neo4j Server
        print("Starting Neo4j server...")
        Popen(["neo4j", "console"], shell=True)

        # Wait for Neo4j Initialization
        time.sleep(10)

        # Open the Default Web Browser
        webbrowser.open("http://127.0.0.1:5000")
        print("Launching browser at http://127.0.0.1:5000")

        # Start Flask App
        print("Starting Flask API...")
        app.run(debug=True, host="0.0.0.0", port=5000)

    except Exception as e:
        print(f"Error starting services: {e}")


# --- Main Entry ---
if __name__ == "__main__":
    start_services()
