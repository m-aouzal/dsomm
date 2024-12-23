import json
from collections import OrderedDict

# Function to deduplicate the file
def deduplicate_file(file_path, output_path):
    with open(file_path, 'r') as file:
        data = json.load(file)

        if not isinstance(data, list):
            raise ValueError("The JSON structure is not a list.")

        # Use OrderedDict to preserve the order and remove duplicates
        unique_entries = OrderedDict()

        for item in data:
            # Create a unique key based on Dimension, Sub Dimension, and Activity
            key = (item['Dimension'], item['Sub Dimension'], item['Activity'])

            # Only add the entry if the description is not empty and either the key is new
            # or the current item has a non-empty description
            if key not in unique_entries or (item['Description'] and unique_entries[key]['Description'] == ""):
                unique_entries[key] = item

        # Convert back to a list for saving
        deduplicated_data = list(unique_entries.values())

        # Save to the output file
        with open(output_path, 'w') as output_file:
            json.dump(deduplicated_data, output_file, indent=4)

        print(f"Deduplicated file created at: {output_path}")
        print(f"Total unique entries: {len(deduplicated_data)}")

# File paths
file_path = './preprocessed_data/dsomm.json'  # Input file
output_path = './preprocessed_data/unique_dsomm.json'  # Output file

# Deduplicate the file
deduplicate_file(file_path, output_path)
