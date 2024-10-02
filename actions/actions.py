from rasa_sdk import Action
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk import Tracker
import csv
import os

class ActionHandleCustomerQuery(Action):

    def name(self) -> str:
        return "action_handle_customer_query"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: dict) -> list:
        
        # Get the user message
        user_message = tracker.latest_message.get('text').strip().lower()

        # Detect language of the query (basic check)
        user_language = 'ta' if any(ord(char) > 127 for char in user_message) else 'en'

        # Get the appropriate response from the CSV file
        response = self.get_response_from_csv(user_message, user_language)

        # Send the response back to the user
        if response:
            dispatcher.utter_message(text=response)
        else:
            dispatcher.utter_message(text="Sorry, I couldn't find an answer to your query.")
        
        return []

    def get_response_from_csv(self, query, lang):
        """
        Reads a CSV file to find the appropriate response to the query.
        """
        csv_file_path = os.path.join(os.path.dirname(__file__), 'queries.csv')

        # Debugging: print the CSV file path to check if it's correct
        print(f"Looking for CSV file at: {csv_file_path}")

        try:
            with open(csv_file_path, mode='r', encoding='utf-8') as file:
                reader = csv.DictReader(file)

                # Preprocess the query to handle case sensitivity and extra spaces
                query = query.strip().lower()

                for row in reader:
                    # Preprocess the CSV query before comparison
                    csv_query = row['query'].strip().lower()

                    # Match both Tamil and English queries from the CSV
                    if csv_query == query and row['language'] == lang:
                        return row['response']
        except FileNotFoundError:
            print(f"CSV file not found: {csv_file_path}")
        except Exception as e:
            print(f"Error reading CSV file: {e}")

        return None
