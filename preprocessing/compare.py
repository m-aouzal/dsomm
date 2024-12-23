import json

# File paths
unique_tools_path = './preprocessed_data/unique_tools.json'
questions_tools_path = './preprocessed_data/questions_unique_tools.json'
output_path = './preprocessed_data/tools_comparison_summary.json'

# Load unique tools from both files
with open(unique_tools_path, 'r') as unique_file:
    unique_tools = {tool.lower().strip() for tool in json.load(unique_file)}

with open(questions_tools_path, 'r') as questions_file:
    questions_tools_raw = {tool.lower().strip() for tool in json.load(questions_file)}
    # Generate a second normalized set with underscores replaced by spaces
    questions_tools_normalized = {tool.replace('_', ' ') for tool in questions_tools_raw}

# Create a union of raw and normalized questions tools for comparison
questions_tools = questions_tools_raw.union(questions_tools_normalized)

# Compare the normalized sets
tools_only_in_unique = unique_tools - questions_tools
tools_only_in_questions = questions_tools - unique_tools

# Display results
print("Tools only in unique_tools.json:")
print(tools_only_in_unique)

print("\nTools only in questions_unique_tools.json:")
print(tools_only_in_questions)

# Prepare a summary of differences
decision_summary = {
    "Tools only in unique_tools.json": list(tools_only_in_unique),
    "Tools only in questions_unique_tools.json": list(tools_only_in_questions),
    "Match Status": "Matching" if not tools_only_in_unique and not tools_only_in_questions else "Mismatch"
}

# Save the decision summary
with open(output_path, 'w') as summary_file:
    json.dump(decision_summary, summary_file, indent=4)

print(f"\nDecision summary saved to {output_path}")
