import os
import json

def upload_configuration() -> dict:
    """
    Function to upload basic settings from a JSON file.
    """
    path = os.path.join(os.path.dirname(__file__), 'settings.json')
    with open(path) as f:
        data = json.load(f)

    return data
