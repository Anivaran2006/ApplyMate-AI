import json

DB_PATH = "app/database/db.json"

def load_data():
    with open(DB_PATH, "r") as file:
        return json.load(file)

def save_data(data):
    with open(DB_PATH, "w") as file:
        json.dump(data, file, indent=4)