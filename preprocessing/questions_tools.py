import json

# File paths
input_file_path = './data/questions.json'  # Replace with your file path
output_file_path = './preprocessed_data/questions_cleaned_tools.json'  # Output file path

# Define a set of known stage or category names to exclude
excluded_values = {
    "ci", "testing", "deployment", "scm", "planning", "containerization", 
    "orchestration", "iac", "policy", "operations", "dast", 
    "backup_recovery", "cloud_security", "monitoring", "code_quality", 
    "artifact_management", "vulnerability_testing", "security_management"
}

# Load the JSON data
with open(input_file_path, 'r') as input_file:
    data = json.load(input_file)

# Extract tools from "options" across all sections
unique_tools = set()
for section in data.get("sections", []):  # Loop through sections
    for question in section.get("questions", []):  # Loop through questions
        for option in question.get("options", []):  # Loop through options
            if "value" in option:
                tool = option["value"].lower().strip()  # Normalize tool names
                # Exclude stage or category names
                if tool not in excluded_values:
                    unique_tools.add(tool)

# Convert to sorted list
unique_tools_list = sorted(unique_tools)

# Save unique tools to a file
with open(output_file_path, 'w') as output_file:
    json.dump(unique_tools_list, output_file, indent=4)

# Display confirmation
print(f"Cleaned unique tools extracted and saved to {output_file_path}")
