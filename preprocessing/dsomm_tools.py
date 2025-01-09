import json
from collections import defaultdict

# Define the file paths
dsomm_file_path = './data/dsomm.json'  # Update this path
grouped_output_file_path = './preprocessed_data/grouped_by_parent.json'  # Grouped tools file
brut_output_file_path = './preprocessed_data/dsomm_tools.json'  # Brute tools file

# Define the exempt list
exempt_list = [
    "HashiCorp Vault",
    "IBM QRadar",
    "AWS IAM (Identity and Access Management)",
    "Azure Active Directory",
    "Google Cloud Resource Manager",
    "Docker Bench for Security",
    "Kubernetes Secrets",
    "Sonatype Nexus Lifecycle",
    "Tripwire",
    "Vault",
    "GitSecrets",
    "TruffleHog"
]

# Description of the exempt list:
# The exempt list includes tools that are unique or specialized and should not be grouped by their first word. 
# These tools often represent standalone functionalities or services and are treated as independent entities 
# during the grouping process. For example, "HashiCorp Vault" is a specific tool and should not be merged 
# with other tools under "HashiCorp" or "Vault."

# Function to generate a brute list of tools
def generate_brut_tools_list(dsomm_data):
    """
    Generates a flat, sorted list of all tools mentioned in the dsomm.json file.
    
    Args:
        dsomm_data (list): The parsed JSON data from dsomm.json.
    
    Returns:
        list: A sorted list of unique tool names.
    """
    tools_set = set()
    for entry in dsomm_data:
        if 'Tools' in entry and isinstance(entry['Tools'], list):
            for tool in entry['Tools']:
                if isinstance(tool, dict) and 'Name' in tool:
                    tools_set.add(tool['Name'])
    return sorted(tools_set)

# Function to group tools by parent
def group_tools_by_parent(dsomm_data, exempt_list):
    """
    Groups tools by their parent name (first word) unless they are in the exempt list.
    Exempt tools retain their full name as their group key.

    Args:
        dsomm_data (list): The parsed JSON data from dsomm.json.
        exempt_list (list): A list of tool names to exempt from parent-based grouping.
    
    Returns:
        dict: A dictionary of grouped tools with parent names as keys.
    """
    grouped_tools = defaultdict(list)
    for entry in dsomm_data:
        if 'Tools' in entry and isinstance(entry['Tools'], list):
            for tool in entry['Tools']:
                if isinstance(tool, dict) and 'Name' in tool:
                    tool_name = tool['Name']
                    # Group by first word if not in exempt list
                    if tool_name in exempt_list:
                        grouped_tools[tool_name].append(tool_name)
                    else:
                        parent = tool_name.split()[0]
                        grouped_tools[parent].append(tool_name)

    # Add git-commit-signing to specific tools
    if "Git" in grouped_tools:
        grouped_tools["Git"].append("git-commit-signing")
    if "GitHub" in grouped_tools:
        grouped_tools["GitHub"].append("git-commit-signing")
    if "GitLab" in grouped_tools:
        grouped_tools["GitLab"].append("git-commit-signing")

    # Ensure unique tools within each group
    grouped_tools = {parent: sorted(set(tools)) for parent, tools in grouped_tools.items()}
    return grouped_tools

# Load the JSON data from the file
with open(dsomm_file_path, 'r') as dsomm_file:
    dsomm_data = json.load(dsomm_file)

# Generate brute tools list
brut_tools = generate_brut_tools_list(dsomm_data)

# Save brute tools list to a file
with open(brut_output_file_path, 'w') as brut_output_file:
    json.dump(brut_tools, brut_output_file, indent=4)
print(f"Brute tools list saved to {brut_output_file_path}")

# Group tools by parent
grouped_tools = group_tools_by_parent(dsomm_data, exempt_list)

# Save grouped tools to a file
with open(grouped_output_file_path, 'w') as grouped_output_file:
    json.dump(grouped_tools, grouped_output_file, indent=4)
print(f"Tools grouped by parent saved to {grouped_output_file_path}")
