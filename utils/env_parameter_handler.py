import json
import os

class KeyValueStore:
    def __init__(self, file_path):
        self.file_path = file_path
        self.data = self._load_data()

    def _load_data(self):
        """Load data from the file."""
        if os.path.exists(self.file_path):
            with open(self.file_path, 'r') as file:
                return json.load(file)
        return {}

    def _save_data(self):
        """Save data to the file."""
        with open(self.file_path, 'w') as file:
            json.dump(self.data, file, indent=4)

    def set(self, key, value):
        """Set a key-value pair."""
        self.data[key] = value
        self._save_data()

    def get(self, key, default=None):
        """Get the value for a key."""
        return self.data.get(key, default)

    def delete(self, key):
        """Delete a key-value pair."""
        if key in self.data:
            del self.data[key]
            self._save_data()

    def keys(self):
        """Get all keys."""
        return list(self.data.keys())

    def values(self):
        """Get all values."""
        return list(self.data.values())

    def items(self):
        """Get all key-value pairs."""
        return list(self.data.items())


APP_DATA = os.getenv('LOCALAPPDATA')
APP_DIRECTORY = os.path.join(APP_DATA, "Digi-Harbinger")
ENV_FILE = os.path.join(APP_DIRECTORY, "env.json")
KeyValueStore = KeyValueStore(ENV_FILE)