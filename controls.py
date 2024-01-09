import os
import json

def upload_configuration()->dict:
    """Func to upload basic se"""
    path = os.path.join(os.path.dirname(__file__), 'settings.json')
    with open(path) as f:
        data = json.load(f)

    return data

