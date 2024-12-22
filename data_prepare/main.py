import json
import os

# Define file paths
DATA_FOLDER = "data"
OUTPUT_FOLDER = "preprocessed_data"
DESCRIPTION_TOOLS_FILE = os.path.join(DATA_FOLDER, "description_tools.json")
EVERYTHING_FILE = os.path.join(DATA_FOLDER, "evrything.json")
OUTPUT_FILE = os.path.join(OUTPUT_FOLDER, "dsomm.json")

# Ensure the output directory exists
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

def load_json(file_path):
    with open(file_path, 'r') as f:
        return json.load(f)

def save_json(data, file_path):
    with open(file_path, 'w') as f:
        json.dump(data, f, indent=4)

def integrate_and_deduplicate_data(everything, description_tools):
    """
    Integrate description tools into the 'everything' dataset and remove redundancy
    based on the unique key: (Dimension, Sub Dimension, Activity, Level).
    """
    # Create a map for unique entries based on the key
    unique_entries = {}
    description_map = {
        (item["Dimension"], item["Sub Dimension"], item["Activity"], item["Level"]): item
        for item in description_tools
    }

    for item in everything:
        key = (item["Dimension"], item["Sub Dimension"], item["Activity"], item["Level"])
        
        # Integrate description tools
        if key in description_map:
            description_entry = description_map[key]
            item["Description"] = description_entry.get("Description", "")
            item["Tools"] = description_entry.get("Tools", [])
        
        # Add to unique entries map
        unique_entries[key] = item

    # Return only the unique values
    return list(unique_entries.values())

def main():
    # Load the JSON files
    everything = load_json(EVERYTHING_FILE)
    description_tools = load_json(DESCRIPTION_TOOLS_FILE)

    # Integrate and deduplicate data
    updated_everything = integrate_and_deduplicate_data(everything, description_tools)

    # Save the deduplicated and integrated data to the output file
    save_json(updated_everything, OUTPUT_FILE)
    print(f"Deduplicated and integrated data saved to {OUTPUT_FILE}")

if __name__ == "__main__":
    main()
