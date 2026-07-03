import os
import json

json_storage = 'conversations.json'

def load_data():
    if os.path.exists(json_storage):
        with open(json_storage, 'r', encoding='utf-8') as file:
            return json.load(file)
    return {}

def save_data(data):
    with open(json_storage, 'w', encoding='utf-8') as file:
        json.dump(data, file, ensure_ascii=False, indent=4)