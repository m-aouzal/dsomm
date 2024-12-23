import json

# File paths
file1_path = './data/evrything.json'  # File 1: everything
file2_path = './data/description_tools.json'  # File 2: description tools
output_file_path = './data/missing_activities.json'  # Output file for missing activities

# Load the data from the files
with open(file1_path, 'r') as file1, open(file2_path, 'r') as file2:
    data1 = json.load(file1)  # Everything.json
    data2 = json.load(file2)  # Description_tools.json

# Create sets of unique activities (including Level) from both files
activities1 = set(
    (item['Dimension'], item['Sub Dimension'], item['Activity'], item['Level'])
    for item in data1
)
activities2 = set(
    (item['Dimension'], item['Sub Dimension'], item['Activity'], item['Level'])
    for item in data2
)

# Find activities in everything.json that are not in description_tools.json
missing_activities = [
    item for item in data1
    if (item['Dimension'], item['Sub Dimension'], item['Activity'], item['Level']) not in activities2
]

# Save missing activities to the new file
with open(output_file_path, 'w') as output_file:
    json.dump(missing_activities, output_file, indent=4)

print(f"Found {len(missing_activities)} activities not in description_tools.json (including Level). Saved to {output_file_path}.")
