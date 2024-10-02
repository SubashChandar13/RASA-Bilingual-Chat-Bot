import subprocess
import time
import requests
import json
import sys

# Start Rasa actions server
subprocess.Popen(["rasa", "run", "actions"])
time.sleep(10)  # Optional: wait for a few seconds to ensure actions server is up

# Start Rasa API server
subprocess.Popen(["rasa", "run", "--enable-api", "--cors", "*"])
time.sleep(30)  # Optional: wait for a few seconds to ensure the Rasa API is up


# Pass the Ngrok URL to your app.py (Flask) and run it
subprocess.run(["python", "app.py"])
