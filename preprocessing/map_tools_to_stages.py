import json
import os

def load_json(file_path):
    """Load JSON data from a file."""
    with open(file_path, 'r') as file:
        return json.load(file)

def save_json(data, file_path):
    """Save JSON data to a file."""
    with open(file_path, 'w') as file:
        json.dump(data, file, indent=2)

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

        # Map tools to their detailed descriptions
        detailed_tools = [
            tool_lookup[tool] for tool in stage_tools if tool in tool_lookup
        ]

        # Update stage with detailed tools
        updated_stage = {
            "stage": stage_name,
            "tools": detailed_tools
        }
        updated_pipeline.append(updated_stage)

    return {"pipeline": updated_pipeline}

def process_pipeline_with_tools(extracted_tools_file, pipeline_file, output_file):
    """
    Process pipeline_order.json and map tools from extracted_tools.json to their respective stages.
    """
    # Check if input files exist
    if not os.path.exists(extracted_tools_file):
        print(f"Error: {extracted_tools_file} does not exist.")
        return

    if not os.path.exists(pipeline_file):
        print(f"Error: {pipeline_file} does not exist.")
        return

    # Load JSON data
    extracted_tools = load_json(extracted_tools_file)
    pipeline_data = load_json(pipeline_file).get("pipeline", [])

    # Map tools to stages
    updated_pipeline = map_tools_to_stages(extracted_tools, pipeline_data)

    # Save the updated pipeline to the output file
    save_json(updated_pipeline, output_file)
    print(f"Updated pipeline saved to {output_file}")

if __name__ == "__main__":
    # Define file paths
    extracted_tools_file = "../data/extracted_tools.json"  # Path to extracted tools file
    pipeline_file = "../data/pipeline_order.json"  # Path to pipeline order file
    output_file = "../data/updated_pipeline_order.json"  # Path to save the updated pipeline

    # Process pipeline mapping
    process_pipeline_with_tools(extracted_tools_file, pipeline_file, output_file)
