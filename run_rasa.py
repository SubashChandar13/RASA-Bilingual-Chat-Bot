import subprocess
import time

def run_rasa_server():
    """Run the Rasa server."""
    subprocess.Popen(["rasa", "run", "--enable-api", "--cors", "*"])

def run_action_server():
    """Run the Rasa action server."""
    subprocess.Popen(["rasa", "run", "actions"])

if __name__ == '__main__':
    run_rasa_server()
    time.sleep(5)  # Optional: Wait for the Rasa server to start
    run_action_server()
    
    print("Rasa server and action server are running...")
    
    # Keep the script running to prevent it from exiting
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("Stopping servers...")
