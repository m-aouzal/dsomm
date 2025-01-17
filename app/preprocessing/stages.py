import json

# Define file paths
pipeline_file_path = './data/pipeline_order.json'
output_file_path = './output/stages.json'

def extract_stages(pipeline_file_path, output_file_path):
    """
    Extracts the stages from the pipeline JSON file and saves them to a JSON file.
    """
    # Load the pipeline JSON
    with open(pipeline_file_path, 'r') as file:
        pipeline_data = json.load(file)
    
    # Extract stages
    stages = [stage["stage"] for stage in pipeline_data["pipeline"]]
    
    # Save stages to output file
    with open(output_file_path, 'w') as output_file:
        json.dump(stages, output_file, indent=4)
    
    print(f"Stages extracted and saved to {output_file_path}")

# Run the function
extract_stages(pipeline_file_path, output_file_path)
