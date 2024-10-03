import subprocess
import time
from flask import Flask, jsonify

app = Flask(__name__)

# Global variables to hold the subprocesses
rasa_actions_process = None
rasa_api_process = None

def start_rasa_actions():
    global rasa_actions_process
    # Start Rasa actions server
    rasa_actions_process = subprocess.Popen(["rasa", "run", "actions"])
    time.sleep(10)  # Wait for a few seconds to ensure actions server is up
    print("Rasa actions server started.")

def start_rasa_api():
    global rasa_api_process
    # Start Rasa API server
    rasa_api_process = subprocess.Popen(["rasa", "run", "--enable-api", "--cors", "*"])
    time.sleep(30)  # Wait for a few seconds to ensure the Rasa API is up
    print("Rasa API server started.")

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
        rasa_actions_process = None
        print("Rasa actions server stopped.")
    
    if rasa_api_process:
        rasa_api_process.terminate()
        rasa_api_process = None
        print("Rasa API server stopped.")

    return jsonify({"message": "Rasa servers stopped successfully."}), 200

@app.route('/')  # Serve the main page or a simple message
def home():
    return jsonify({"message": "Welcome to the Flask app that manages Rasa servers."}), 200

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000, debug=True)


