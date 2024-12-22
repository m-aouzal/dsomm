def get_tools_with_activities(data):
    """Retrieve tools and their associated activities from the JSON data."""
    tool_activities = {}
    for entry in data:
        tools = entry.get("Tools", "").split(", ")  # Assuming "Tools" is a comma-separated string
        for tool in tools:
            if tool:  # Skip empty tool entries
                tool_activities.setdefault(tool, []).append(entry["Activity"])
    return tool_activities

def display_tools_with_activities(tool_activities):
    """Display tools and their associated activities."""
    for tool, activities in tool_activities.items():
        print(f"Tool: {tool}")
        print("  Activities:")
        for activity in activities:
            print(f"    - {activity}")
        print("-" * 40)
