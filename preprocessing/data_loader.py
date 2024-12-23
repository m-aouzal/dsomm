import json

def load_json(file_path):
    """Load data from a JSON file."""
    try:
        with open(file_path, 'r') as file:
            return json.load(file)
    except FileNotFoundError:
        print(f"Error: The file {file_path} does not exist.")
        return []
    except json.JSONDecodeError:
        print(f"Error: The file {file_path} is not a valid JSON.")
        return []

def save_json(data, file_path):
    """Write data to a JSON file."""
    try:
        with open(file_path, 'w') as file:
            json.dump(data, file, indent=4)
        print(f"Data successfully saved to {file_path}.")
    except Exception as e:
        print(f"Error saving data: {e}")
