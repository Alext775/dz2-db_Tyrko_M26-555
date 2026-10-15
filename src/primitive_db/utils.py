import json
import os

from .constants import DATA_DIR


def load_metadata(filepath):
    try:
        with open(filepath, encoding="utf-8") as file:
            return json.load(file)
    except FileNotFoundError:
        return {}


def save_metadata(filepath, data):
    with open(filepath, "w", encoding="utf-8") as file:
        json.dump(data, file, ensure_ascii=False, indent=4)


def load_table_data(table_name):
    filepath = os.path.join(DATA_DIR, f"{table_name}.json")

    try:
        with open(filepath, encoding="utf-8") as file:
            return json.load(file)
    except FileNotFoundError:
        return []


def save_table_data(table_name, data):
    os.makedirs(DATA_DIR, exist_ok=True)
    filepath = os.path.join(DATA_DIR, f"{table_name}.json")

    with open(filepath, "w", encoding="utf-8") as file:
        json.dump(data, file, ensure_ascii=False, indent=4)


def remove_table_data(table_name):
    filepath = os.path.join(DATA_DIR, f"{table_name}.json")

    try:
        os.remove(filepath)
    except FileNotFoundError:
        pass
