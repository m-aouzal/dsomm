import json

# Define the file path
dsomm_file_path = './data/dsomm.json'  # Update this path
output_file_path = './preprocessed_data/unique_tools.json'  # Output file path

# Load the JSON data from the file
with open(dsomm_file_path, 'r') as dsomm_file:
    dsomm_data = json.load(dsomm_file)

# Extract unique tools based on their "Name"
tools_set = set()
for entry in dsomm_data:
    if 'Tools' in entry and isinstance(entry['Tools'], list):
        tools_set.update(tool['Name'] for tool in entry['Tools'] if isinstance(tool, dict) and 'Name' in tool)

# Convert the set to a sorted list of unique tool names
unique_tools = sorted(tools_set)

# Save the unique tools to a file
with open(output_file_path, 'w') as output_file:
    json.dump(unique_tools, output_file, indent=4)

# Display confirmation
print(f"Unique tools saved to {output_file_path}")
