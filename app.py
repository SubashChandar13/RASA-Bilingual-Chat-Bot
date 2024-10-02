import speech_recognition as sr
import requests
import pyttsx3
from gtts import gTTS
import pygame
import os
from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
import threading

# Initialize pygame mixer
pygame.mixer.init()

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Dynamically set the Rasa server URL
RASA_SERVER_URL = "http://localhost:5005/webhooks/rest/webhook"  # Update with your Rasa server URL
print(RASA_SERVER_URL)

# Initialize pyttsx3 for English voice responses
engine = pyttsx3.init()
# Create a lock for thread safety
speak_lock = threading.Lock()

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
    def speak():
        if lang == 'ta':
            tts = gTTS(text=response_text, lang='ta')
            tts.save("response.mp3")

            # Play the audio using pygame
            pygame.mixer.music.load("response.mp3")
            pygame.mixer.music.play()

            # Wait until the audio finishes playing
            while pygame.mixer.music.get_busy():
                pygame.time.Clock().tick(10)  # Ensure it waits until audio is done

            # Clean up
            pygame.mixer.music.unload()
            os.remove("response.mp3")
        else:
            with speak_lock:  # Use the lock to ensure thread safety
                engine.say(response_text)
                engine.runAndWait()

    # Run the speech function in a separate thread
    speech_thread = threading.Thread(target=speak)
    speech_thread.start()

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
