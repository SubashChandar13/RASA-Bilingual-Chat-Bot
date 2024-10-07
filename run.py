import subprocess
import time
import os
import requests  # Import requests library
from flask import Flask, jsonify, render_template
from flask_cors import CORS

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Global variables to hold the subprocesses
rasa_actions_process = None
rasa_api_process = None

def start_rasa_actions():
    global rasa_actions_process
    try:
        # Start Rasa actions server
        rasa_actions_process = subprocess.Popen(
            ["rasa", "run", "actions"], 
            stdout=subprocess.PIPE, 
            stderr=subprocess.PIPE
        )
        time.sleep(10)  # Wait for a few seconds to ensure actions server is up
        print("Rasa actions server started.")
    except Exception as e:
        print(f"Error starting Rasa actions server: {e}")

def start_rasa_api():
    global rasa_api_process
    try:
        # Start Rasa API server
        rasa_api_process = subprocess.Popen(
            ["rasa", "run", "--enable-api", "--cors", "*"], 
            stdout=subprocess.PIPE, 
            stderr=subprocess.PIPE
        )
        time.sleep(10)  # Wait for a few seconds to ensure the Rasa API is up
        print("Rasa API server started.")
    except Exception as e:
        print(f"Error starting Rasa API server: {e}")

@app.route('/start_rasa', methods=["POST"])
def start_rasa():
    if rasa_actions_process is None:
        start_rasa_actions()
    else:
        return jsonify({"message": "Rasa actions server is already running."}), 400

    if rasa_api_process is None:
        start_rasa_api()
    else:
        return jsonify({"message": "Rasa API server is already running."}), 400

    return jsonify({"message": "Rasa servers started successfully."}), 200

@app.route('/stop_rasa', methods=["POST"])
def stop_rasa():
    global rasa_actions_process, rasa_api_process
    if rasa_actions_process:
        rasa_actions_process.terminate()
        rasa_actions_process.wait()  # Wait for the process to terminate
        rasa_actions_process = None
        print("Rasa actions server stopped.")
    
    if rasa_api_process:
        rasa_api_process.terminate()
        rasa_api_process.wait()  # Wait for the process to terminate
        rasa_api_process = None
        print("Rasa API server stopped.")

    return jsonify({"message": "Rasa servers stopped successfully."}), 200

@app.route('/check_rasa', methods=["GET"])  # Health check endpoint
def check_rasa():
    try:
        # Check if Rasa API is running
        response = requests.get("http://localhost:5005/status")
        if response.status_code == 200:
            return jsonify({"message": "Rasa API is running", "status": response.json()}), 200
        else:
            return jsonify({"message": "Rasa API is not running", "status_code": response.status_code}), 500
    except requests.exceptions.RequestException as e:
        return jsonify({"message": "Error checking Rasa API status", "error": str(e)}), 500

@app.route('/')  # Serve the main page or a simple message
def home():
    return render_template('rasa.html')  # Render the HTML page

if __name__ == "__main__":
    port = int(os.environ.get('PORT', 5000))  # Use the port assigned by Render
    app.run(host='0.0.0.0', port=port, debug=True) 
