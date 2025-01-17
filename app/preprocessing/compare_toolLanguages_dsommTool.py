import json

# File paths
dsomm_tools_path = './data/dsomm_tools.json'  # Update this path to the actual location
tool_languages_path = './data/tool_languages.json'  # Update this path to the actual location
output_path = './output/comparison_summary.json'  # Output path for results

# Load tools from dsomm_tools.json
with open(dsomm_tools_path, 'r') as dsomm_file:
    dsomm_tools = {tool.lower().strip() for tool in json.load(dsomm_file)}

# Load tools from tool_languages.json
with open(tool_languages_path, 'r') as tool_lang_file:
    tool_languages = {tool.lower().strip() for tool in json.load(tool_lang_file)}

# Compare the two sets
tools_only_in_dsomm = dsomm_tools - tool_languages
tools_only_in_tool_lang = tool_languages - dsomm_tools

# Print the results for debugging
print("Tools only in dsomm_tools.json:")
print(tools_only_in_dsomm)

print("\nTools only in tool_languages.json:")
print(tools_only_in_tool_lang)

# Prepare a summary of differences
comparison_summary = {
    "Tools only in dsomm_tools.json": sorted(tools_only_in_dsomm),
    "Tools only in tool_languages.json": sorted(tools_only_in_tool_lang),
    "Match Status": "Matching" if not tools_only_in_dsomm and not tools_only_in_tool_lang else "Mismatch"
}

# Save the comparison summary to a JSON file
with open(output_path, 'w') as summary_file:
    json.dump(comparison_summary, summary_file, indent=4)

print(f"\nComparison summary saved to {output_path}")
