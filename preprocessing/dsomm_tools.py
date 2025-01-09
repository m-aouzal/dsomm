import json
from collections import defaultdict

# Define the file paths
dsomm_file_path = './data/dsomm.json'  # Update this path
grouped_output_file_path = './preprocessed_data/grouped_by_parent.json'  # Grouped tools file
brut_output_file_path = './preprocessed_data/dsomm_tools.json'  # Brute tools file

# Exempt list
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

# Recursively extract tools from nested structures
def extract_tools(data, tools_set):
    """
    Recursively extract tools from nested dictionaries and lists.
    """
    if isinstance(data, list):
        for item in data:
            extract_tools(item, tools_set)
    elif isinstance(data, dict):
        if 'Tools' in data and isinstance(data['Tools'], list):
            for tool in data['Tools']:
                if isinstance(tool, dict) and 'Name' in tool:
                    tools_set.add(tool['Name'].strip())
        else:
            for key, value in data.items():
                extract_tools(value, tools_set)

# Function to generate a brute list of tools
def generate_brut_tools_list(dsomm_data):
    """
    Generates a flat, sorted list of all tools mentioned in the dsomm.json file.
    """
    tools_set = set()
    extract_tools(dsomm_data, tools_set)
    return sorted(tools_set)

# Function to group tools by parent
def group_tools_by_parent(tools_list, exempt_list):
    """
    Groups tools by their parent name (first word) unless they are in the exempt list.
    """
    grouped_tools = defaultdict(list)

    for tool_name in tools_list:
        if tool_name in exempt_list:
            grouped_tools[tool_name].append(tool_name)
        else:
            parent = tool_name.split()[0]  # Use the first word as the parent
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
grouped_tools = group_tools_by_parent(brut_tools, exempt_list)

# Save grouped tools to a file
with open(grouped_output_file_path, 'w') as grouped_output_file:
    json.dump(grouped_tools, grouped_output_file, indent=4)
print(f"Tools grouped by parent saved to {grouped_output_file_path}")
