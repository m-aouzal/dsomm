import json
import os

SCRIPT_DIR = os.path.dirname(os.path.realpath(__file__))

# Construct absolute paths relative to the script's location
PIPELINE_ORDER_FILE = os.path.join(SCRIPT_DIR, "..", "data", "pipeline_order.json")
TOOL_ACTIVITIES_FILE = os.path.join(SCRIPT_DIR, "..", "data", "tool_activities.json")
STAGE_DEFAULTS_FILE = os.path.join(SCRIPT_DIR, "..", "data", "stage_defaults.json")


def generate_stage_defaults(pipeline_order_file, tool_activities_file, output_file):
    """
    Generates a stage_defaults.json file that lists the unique activities
    associated with each stage in the pipeline.

    Args:
        pipeline_order_file: Path to the pipeline_order.json file.
        tool_activities_file: Path to the tool_activities.json file.
        output_file: Path to the output stage_defaults.json file.
    """
    try:
        with open(pipeline_order_file, "r") as f:
            pipeline_data = json.load(f)
        with open(tool_activities_file, "r") as f:
            tool_activities_data = json.load(f)
    except FileNotFoundError as e:
        print(f"Error: File not found - {e}")
        return

    stage_defaults = {}

    for stage_entry in pipeline_data["pipeline"]:
        stage_name = stage_entry["stage"]
        stage_defaults[stage_name] = {
            "activities": []  # Only store a list of activity names
        }
        tools = stage_entry["tools"]

        stage_activities = set()  # Use a set to store unique activities

        for tool_name in tools:
            if tool_name in tool_activities_data:
                tool_activities = tool_activities_data[tool_name].get("Activities", [])
                for activity in tool_activities:
                    activity_name = activity.get("Activity")
                    if activity_name:
                        stage_activities.add(activity_name)  # Add to the set

        # Convert the set to a list for JSON serialization
        stage_defaults[stage_name]["activities"] = list(stage_activities)

    with open(output_file, "w") as f:
        json.dump(stage_defaults, f, indent=4)

    print(f"Successfully generated {output_file}")


if __name__ == "__main__":
    generate_stage_defaults(PIPELINE_ORDER_FILE, TOOL_ACTIVITIES_FILE, STAGE_DEFAULTS_FILE)