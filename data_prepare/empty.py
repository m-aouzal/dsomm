import json

# Function to count and save items with empty descriptions
def save_empty_descriptions(file_path, output_path):
    with open(file_path, 'r') as file:
        data = json.load(file)
        # Filter items with an empty description
        empty_description_items = [
            item for item in data if item.get('Description', "") == ""
        ]
        
        # Save the filtered items to a new file
        with open(output_path, 'w') as output_file:
            json.dump(empty_description_items, output_file, indent=4)
        
        return len(empty_description_items), empty_description_items

# File paths
file_path = './preprocessed_data/unique_dsomm.json'  # Input file path
output_path = './empty.json'  # Output file path

# Execute the function and get results
empty_description_count, empty_description_items = save_empty_descriptions(file_path, output_path)

# Print the count and confirmation message
print(f"Number of items with empty Description: {empty_description_count}")
print(f"Items with empty Description saved to {output_path}")
