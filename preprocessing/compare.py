import json
import re

# File paths
pipeline_order_path = './data/pipeline_order.json'  # Path to pipeline_order.json
unique_tools_path = './preprocessed_data/dsomm_tools.json'  # Path to dsomm_tools.json
output_path = './output/decision_summary.json'  # Output path for the decision summary

# Function to normalize tool names
def normalize_tool_name(tool_name):
    """
    Normalizes a tool name by:
    - Converting to lowercase.
    - Stripping leading/trailing whitespace.
    - Replacing underscores with spaces.
    - Collapsing multiple spaces into a single space.
    Args:
        tool_name (str): The tool name to normalize.
    Returns:
        str: The normalized tool name.
    """
    tool_name = tool_name.lower().strip()
    tool_name = tool_name.replace('_', ' ')
    tool_name = re.sub(r'\s+', ' ', tool_name)  # Replace multiple spaces with a single space
    return tool_name

# Step 1: Extract tools from pipeline_order.json and normalize
def extract_pipeline_tools(pipeline_order_path):
    """
    Extracts all tools from pipeline_order.json and ensures uniqueness with normalization.
    
    Args:
        pipeline_order_path (str): Path to the pipeline_order.json file.
    
    Returns:
        set: A set of normalized tool names extracted from the pipeline_order.json file.
    """
    with open(pipeline_order_path, 'r') as pipeline_file:
        pipeline_data = json.load(pipeline_file)
        tools = set()
        for stage in pipeline_data.get("pipeline", []):
            for tool in stage.get("tools", []):
                tools.add(normalize_tool_name(tool))
        return tools

# Step 2: Load and normalize tools from dsomm_tools.json
def load_unique_tools(unique_tools_path):
    """
    Loads and normalizes unique tools from dsomm_tools.json.
    
    Args:
        unique_tools_path (str): Path to the dsomm_tools.json file.
    
    Returns:
        set: A set of normalized tool names from the dsomm_tools.json file.
    """
    with open(unique_tools_path, 'r') as unique_file:
        return {normalize_tool_name(tool) for tool in json.load(unique_file)}

# Step 3: Compare the two sets of tools
def compare_tools(pipeline_tools, dsomm_tools):
    """
    Compares tools between pipeline_order.json and dsomm_tools.json.
    
    Args:
        pipeline_tools (set): A set of normalized tools extracted from pipeline_order.json.
        dsomm_tools (set): A set of normalized tools loaded from dsomm_tools.json.
    
    Returns:
        dict: A summary of differences between the two sets.
    """
    tools_only_in_pipeline = pipeline_tools - dsomm_tools
    tools_only_in_dsomm = dsomm_tools - pipeline_tools

    return {
        "Tools only in pipeline_order.json": sorted(list(tools_only_in_pipeline)),
        "Tools only in dsomm_tools.json": sorted(list(tools_only_in_dsomm)),
        "Match Status": "Matching" if not tools_only_in_pipeline and not tools_only_in_dsomm else "Mismatch"
    }

# Step 4: Main process
if __name__ == "__main__":
    # Extract tools from pipeline_order.json
    pipeline_tools = extract_pipeline_tools(pipeline_order_path)
    
    # Load tools from dsomm_tools.json
    dsomm_tools = load_unique_tools(unique_tools_path)
    
    # Compare the tools
    comparison_summary = compare_tools(pipeline_tools, dsomm_tools)
    
    # Display the results
    print("Tools only in pipeline_order.json:")
    print(comparison_summary["Tools only in pipeline_order.json"])
    
    print("\nTools only in dsomm_tools.json:")
    print(comparison_summary["Tools only in dsomm_tools.json"])
    
    # Save the comparison summary
    with open(output_path, 'w') as output_file:
        json.dump(comparison_summary, output_file, indent=4)
    
    print(f"\nComparison summary saved to {output_path}")
