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

def map_tools_to_stages(extracted_tools, pipeline_data):
    """
    Map tools from extracted_tools.json to their appropriate stages in pipeline_order.json.
    """
    # Convert extracted tools to a dictionary for easy lookup by tool name
    tool_lookup = {tool["Name"]: tool for tool in extracted_tools}

    updated_pipeline = []
    for stage in pipeline_data:
        stage_name = stage.get("stage", "")
        stage_tools = stage.get("tools", [])

        # Handle case where tools in stage_tools are dictionaries
        if stage_tools and isinstance(stage_tools[0], dict):
            # Extract tool names from the dictionaries
            tool_names = [tool.get("Name", "") for tool in stage_tools]
        else:
            tool_names = stage_tools  # Assume it's a list of strings

        # Map tools to their detailed descriptions
        detailed_tools = [
            tool_lookup[tool] for tool in tool_names if tool in tool_lookup
        ]

        # Update stage with detailed tools
        updated_stage = {
            "stage": stage_name,
            "tools": detailed_tools
        }
        updated_pipeline.append(updated_stage)

    return {"pipeline": updated_pipeline}

def preprocess_dsomm(input_file, pipeline_file, output_dir):
    """
    Preprocess the dsomm.json file and generate:
      - level_activities.json
      - tool_activities.json
      - report_levels.json
      - extracted_tools.json
      - updated_pipeline_order.json
    """
    # Check if the input file exists
    if not os.path.exists(input_file):
        print(f"Error: The file {input_file} does not exist.")
        return

    if not os.path.exists(pipeline_file):
        print(f"Error: The file {pipeline_file} does not exist.")
        return

    # Load the original dsomm.json and pipeline_order.json
    dsomm_data = load_json(input_file)
    pipeline_data = load_json(pipeline_file).get("pipeline", [])
    if not dsomm_data:
        print("Error: No data loaded from dsomm.json.")
        return

    # Generate extracted tools
    extracted_tools = extract_tools(dsomm_data)
    extracted_tools_path = os.path.join(output_dir, "extracted_tools.json")
    save_json(extracted_tools, extracted_tools_path)
    print(f"Extracted tools saved to {extracted_tools_path}")

    # Map tools to pipeline stages
    updated_pipeline = map_tools_to_stages(extracted_tools, pipeline_data)
    updated_pipeline_path = os.path.join(output_dir, "updated_pipeline_order.json")
    save_json(updated_pipeline, updated_pipeline_path)
    print(f"Updated pipeline saved to {updated_pipeline_path}")

if __name__ == "__main__":
    # Define file paths
    input_file = "../data/dsomm.json"  # Path to dsomm.json
    pipeline_file = "../data/pipeline_order.json"  # Path to pipeline_order.json
    output_dir = "./preprocessed_data"  # Output directory

    # Ensure output directory exists
    os.makedirs(output_dir, exist_ok=True)

    # Run preprocessing
    preprocess_dsomm(input_file, pipeline_file, output_dir)
