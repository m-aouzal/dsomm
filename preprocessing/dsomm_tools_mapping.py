import json

# Define file paths
dsomm_file_path = './data/dsomm.json'
pipeline_order_file_path = './data/pipeline_order.json'
output_file_path = './output/tools_activities_mapping_with_details.json'

# Extract tools mapped to activities with possible stages and additional details
def extract_tools_with_details(dsomm_file_path, pipeline_order_file_path, output_file_path):
    with open(dsomm_file_path, 'r') as dsomm_file:
        dsomm_data = json.load(dsomm_file)

    with open(pipeline_order_file_path, 'r') as pipeline_file:
        pipeline_data = json.load(pipeline_file)

    # Create a mapping of tools to their stages based on the pipeline
    stage_mapping = {}
    for stage_entry in pipeline_data["pipeline"]:
        stage_name = stage_entry["stage"]
        for tool in stage_entry["tools"]:
            stage_mapping.setdefault(tool, []).append(stage_name)

    tools_mapping = {}

    for entry in dsomm_data:
        if "Tools" in entry and "Activity" in entry:
            activity = entry["Activity"]
            description = entry.get("Description", "")
            dimension = entry.get("Dimension", "")
            sub_dimension = entry.get("Sub Dimension", "")
            tools = entry["Tools"]

            for tool in tools:
                tool_name = tool["Name"]
                if tool_name not in tools_mapping:
                    tools_mapping[tool_name] = {
                        "Activities": [],
                        "PossibleStages": stage_mapping.get(tool_name, [])  # Add possible stages
                    }
                tools_mapping[tool_name]["Activities"].append({
                    "Activity": activity,
                    "Description": description,
                    "Dimension": dimension,
                    "SubDimension": sub_dimension,
                    "Stages": []  # Leave stages empty for manual editing
                })

    # Filter out tools that are mapped to only one stage
    filtered_tools_mapping = {
        tool: data for tool, data in tools_mapping.items()
        if len(data["PossibleStages"]) > 1
    }

    # Save the mapping to a file
    with open(output_file_path, 'w') as output_file:
        json.dump(filtered_tools_mapping, output_file, indent=4)
    print(f"Filtered tools and activities mapping with details saved to {output_file_path}")

# Run the extraction
extract_tools_with_details(dsomm_file_path, pipeline_order_file_path, output_file_path)
