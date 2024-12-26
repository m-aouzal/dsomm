import os
import json
from data_loader import load_json, save_json

def extract_tools(dsomm_data):
    """
    Extract all tools from the dsomm.json file and save them as a standalone JSON.
    """
    extracted_tools = []
    for entry in dsomm_data:
        if not isinstance(entry, dict):
            print(f"Skipping non-dictionary entry: {entry}")
            continue

        tools = entry.get("Tools", [])
        for tool in tools:
            if isinstance(tool, dict):  # Ensure it's a dictionary
                tool_entry = {
                    "Name": tool.get("Name", ""),
                    "Description": tool.get("Description", ""),
                    "Opensource": tool.get("Opensource", None),
                    "Languages": tool.get("Languages", [])
                }
                if tool_entry not in extracted_tools:
                    extracted_tools.append(tool_entry)
    return extracted_tools

def generate_tool_activities(dsomm_data):
    """
    Generate a mapping of tools to activities, keeping only relevant fields in activities:
    Dimension, Sub Dimension, Activity, Level, and Description.
    """
    tool_activities = {}
    for entry in dsomm_data:
        if not isinstance(entry, dict):
            print(f"Skipping non-dictionary entry: {entry}")
            continue

        tools = entry.get("Tools", [])  # Default to an empty list if "Tools" is missing
        for tool in tools:
            if isinstance(tool, dict):  # Ensure it's a dictionary
                tool_name = tool.get("Name", "")
                if tool_name:  # Skip if the name is empty
                    if tool_name not in tool_activities:
                        tool_activities[tool_name] = {
                            "Description": tool.get("Description", ""),  # Use provided description
                            "Activities": []
                        }
                    # Add only relevant activity details
                    tool_activities[tool_name]["Activities"].append({
                        "Dimension": entry.get("Dimension", ""),
                        "Sub Dimension": entry.get("Sub Dimension", ""),
                        "Activity": entry.get("Activity", ""),
                        "Level": entry.get("Level", ""),
                        "Description": entry.get("Description", "")
                    })
    return tool_activities

def generate_tools_free_report(dsomm_data):
    """
    Generate a report of activities without any associated tools, grouped by level.
    """
    report_levels = {}
    for entry in dsomm_data:
        if not isinstance(entry, dict):
            print(f"Skipping non-dictionary entry: {entry}")
            continue

        tools = entry.get("Tools", [])
        if not tools:  # Include only entries where Tools is empty
            level = int(entry.get("Level", 0))
            if level not in report_levels:
                report_levels[level] = []
            # Add the activity without the Tools field
            tool_free_activity = {k: v for k, v in entry.items() if k != "Tools"}
            report_levels[level].append(tool_free_activity)
    return report_levels

def generate_level_activities(dsomm_data):
    """
    Generate a mapping of levels to activities, preserving all fields.
    """
    level_activities = {}
    for entry in dsomm_data:
        if not isinstance(entry, dict):
            print(f"Skipping non-dictionary entry: {entry}")
            continue

        level = int(entry.get("Level", 0))
        if level not in level_activities:
            level_activities[level] = []
        level_activities[level].append(entry)
    return level_activities

def preprocess_dsomm(input_file, output_dir):
    """
    Preprocess the dsomm.json file and generate:
      - level_activities.json
      - tool_activities.json
      - report_levels.json
      - extracted_tools.json
    """
    # Check if the input file exists
    if not os.path.exists(input_file):
        print(f"Error: The file {input_file} does not exist.")
        return

    # Load the original dsomm.json
    dsomm_data = load_json(input_file)
    if not dsomm_data:
        print("Error: No data loaded from dsomm.json.")
        return

    # Generate mappings
    level_activities = generate_level_activities(dsomm_data)
    tool_activities = generate_tool_activities(dsomm_data)
    report_levels = generate_tools_free_report(dsomm_data)
    extracted_tools = extract_tools(dsomm_data)

    # Ensure output directory exists
    os.makedirs(output_dir, exist_ok=True)

    # Save generated files
    level_activities_path = os.path.join(output_dir, "level_activities.json")
    tool_activities_path = os.path.join(output_dir, "tool_activities.json")
    report_levels_path = os.path.join(output_dir, "report_levels.json")
    extracted_tools_path = os.path.join(output_dir, "extracted_tools.json")

    save_json(level_activities, level_activities_path)
    save_json(tool_activities, tool_activities_path)
    save_json(report_levels, report_levels_path)
    save_json(extracted_tools, extracted_tools_path)

    print("Preprocessing complete. Files saved:")
    print(f"  - {level_activities_path}")
    print(f"  - {tool_activities_path}")
    print(f"  - {report_levels_path}")
    print(f"  - {extracted_tools_path}")

if __name__ == "__main__":
    # Define file paths
    input_file = "../data/dsomm.json"  # Adjusted to the correct path
    output_dir = "../data./preprocessed_data"  # Output folder

    # Run preprocessing
    preprocess_dsomm(input_file, output_dir)
