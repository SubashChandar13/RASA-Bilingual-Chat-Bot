import csv
from rasa.engine.recipes.default_recipe import DefaultV1Recipe
from rasa.engine.storage.storage import ModelStorage
from rasa.engine.storage.resource import Resource
from rasa.shared.nlu.training_data.message import Message
from rasa.shared.nlu.training_data.training_data import TrainingData
from rasa.shared.nlu.constants import TEXT
from rasa.engine.graph import GraphComponent, ExecutionContext
from typing import Any, Dict, List, Text


@DefaultV1Recipe.register(
    DefaultV1Recipe.ComponentType.MESSAGE_FEATURIZER, is_trainable=False
)
class TamilSpokenToWrittenComponent(GraphComponent):
    def __init__(self, config: Dict[Text, Any]) -> None:
        self.config = config
        self.spoken_to_written_dict = self.load_spoken_to_written_mapping(self.config.get("csv_file_path"))

    def load_spoken_to_written_mapping(self, csv_file_path: Text) -> Dict[Text, Text]:
        """Load the mapping of spoken Tamil to written Tamil from a CSV file."""
        spoken_to_written = {}
        try:
            # Load CSV and create the mapping
            with open(csv_file_path, mode='r', encoding='utf-8') as file:
                reader = csv.reader(file)
                next(reader)  # Skip the header row
                for row in reader:
                    if len(row) < 2:
                        continue  # Skip incomplete rows
                    spoken_query, formal_query = row
                    spoken_to_written[spoken_query.strip()] = formal_query.strip()
        except FileNotFoundError:
            print(f"CSV file not found at: {csv_file_path}")
        except Exception as e:
            print(f"Error loading CSV file: {e}")
        return spoken_to_written

    def process(self, messages: List[Message]) -> List[Message]:
        """Process incoming messages and normalize spoken Tamil to written Tamil."""
        for message in messages:
            original_text = message.get(TEXT)
            if original_text:
                normalized_text = self.normalize_text(original_text)
                message.set(TEXT, normalized_text)
        return messages

    def process_training_data(self, training_data: TrainingData) -> TrainingData:
        """Process training data by normalizing spoken Tamil to written Tamil."""
        for example in training_data.training_examples:
            original_text = example.get(TEXT)
            if original_text:
                normalized_text = self.normalize_text(original_text)
                example.set(TEXT, normalized_text)
        return training_data

    def normalize_text(self, text: Text) -> Text:
        """Normalize spoken Tamil to written Tamil using the loaded dictionary."""
        for spoken, written in self.spoken_to_written_dict.items():
            text = text.replace(spoken, written)
        return text

    @classmethod
    def create(
        cls, config: Dict[Text, Any], model_storage: ModelStorage, resource: Resource, execution_context: ExecutionContext
    ) -> GraphComponent:
        """Factory method for creating an instance of the component."""
        return cls(config)
