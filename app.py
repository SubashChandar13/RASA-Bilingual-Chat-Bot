import subprocess
import speech_recognition as sr
import requests
from gtts import gTTS
import os
from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
import threading
from pydub import AudioSegment
from pydub.playback import play  # You can also use ffplay directly
import time

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Dynamically set the Rasa server URL
RASA_SERVER_URL = "http://localhost:5005/webhooks/rest/webhook"  # Update with your Rasa server URL
print(RASA_SERVER_URL)

# Global variable to hold the Rasa process
rasa_process = None

# Create a lock for thread safety
speak_lock = threading.Lock()

def start_rasa():
    global rasa_process
    # Start Rasa server in a subprocess
    rasa_process = subprocess.Popen(
        ['rasa', 'run', '--enable-api', '--cors', '*', '--model', 'models'],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )
    # Give Rasa some time to start up
    time.sleep(10)

def recognize_speech(lang):
    recognizer = sr.Recognizer()
    mic = sr.Microphone()
    with mic as source:
        print("Listening...")
        recognizer.adjust_for_ambient_noise(source)
        audio = recognizer.listen(source)

    try:
        # Recognize speech based on the selected language
        text = recognizer.recognize_google(audio, language=lang)
        print(f"You said: {text}")
        return text
    except sr.UnknownValueError:
        print("Sorry, I did not understand that.")
        return None
    except sr.RequestError as e:
        print(f"Speech recognition request failed: {e}")
        return None

def send_to_rasa(text):
    payload = {
        "sender": "user",
        "message": text
    }

    try:
        response = requests.post(RASA_SERVER_URL, json=payload)
        if response.status_code == 200:
            return response.json()
        else:
            print(f"Failed to get response from Rasa. Status code: {response.status_code}")
            return None
    except requests.exceptions.RequestException as e:
        print(f"Error connecting to Rasa: {e}")
        return None

def speak_response(response_text, lang):
    # Generate audio using gTTS
    if lang == 'ta':
        tts = gTTS(text=response_text, lang='ta')
    else:
        tts = gTTS(text=response_text, lang='en')

    # Save the audio file
    audio_file = "response.mp3"
    tts.save(audio_file)

    # Load and play the audio file using Pydub
    audio = AudioSegment.from_mp3(audio_file)
    play(audio)  # Play the audio

@app.route('/start_rasa', methods=["POST"])
def start_rasa_server():
    if rasa_process is None:
        start_rasa()
        return jsonify({"message": "Rasa server started."}), 200
    else:
        return jsonify({"message": "Rasa server is already running."}), 400

@app.route('/select_language', methods=["POST"])
def select_language():
    data = request.json
    choice = data.get("language")

    if choice == '1':
        return jsonify({"lang_code": 'en-IN', "lang": 'en'})
    elif choice == '2':
        return jsonify({"lang_code": 'ta-IN', "lang": 'ta'})
    else:
        return jsonify({"error": "Invalid choice"}), 400

@app.route('/recognize_speech', methods=["POST"])
def recognize_speech_route():
    data = request.json
    lang = data.get("lang_code", "en-IN")

    user_text = recognize_speech(lang)
    if user_text:
        return jsonify({"text": user_text})
    else:
        return jsonify({"error": "Failed to recognize speech"}), 400

@app.route('/send_message', methods=["POST"])
def send_message():
    data = request.json
    user_text = data.get("message")
    lang = data.get("lang", "en")

    responses = send_to_rasa(user_text)
    if responses:
        for response in responses:
            if 'text' in response:
                speak_response(response['text'], lang)
                return jsonify({"bot_response": response['text']})
            else:
                return jsonify({"error": "No valid text response from Rasa"}), 500
    else:
        return jsonify({"error": "Failed to get response from Rasa"}), 500

@app.route('/')  # Serve the main page
def home():
    return render_template('index.html')  # Serve the HTML file

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5001, debug=True)
