import subprocess
import time
from flask import Flask, jsonify, render_template

app = Flask(__name__)

# Global variable to hold the subprocess
rasa_process = None

def start_rasa():
    global rasa_process
    # Start both Rasa API and actions server in the same process
    rasa_process = subprocess.Popen(
        ["rasa", "run", "--enable-api", "--cors", "*", "--actions", "actions"]
    )
    time.sleep(10)  # Wait for a few seconds to ensure servers are up
    print("Rasa API and actions server started.")

@app.route('/start_rasa', methods=["POST"])
def start_rasa_endpoint():
    if rasa_process is None:
        start_rasa()
    else:
        return jsonify({"message": "Rasa servers are already running."}), 400

    return jsonify({"message": "Rasa servers started successfully."}), 200

@app.route('/stop_rasa', methods=["POST"])
def stop_rasa():
    global rasa_process
    if rasa_process:
        rasa_process.terminate()
        rasa_process = None
        print("Rasa API and actions server stopped.")
        return jsonify({"message": "Rasa servers stopped successfully."}), 200
    else:
        return jsonify({"message": "Rasa servers are not running."}), 400

@app.route('/')  # Serve the main page or a simple message
def home():
    return render_template('rasa.html')  # Render the HTML page

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000, debug=True)
