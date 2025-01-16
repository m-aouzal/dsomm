from flask import Blueprint, render_template, session
import json

summary = Blueprint('summary', __name__)

USER_RESPONSES_FILE = "./data/user_responses.json"
PIPELINE_ORDER_FILE = "./data/pipeline_order.json"

def load_json(file_path):
    with open(file_path, 'r') as file:
        return json.load(file)

pipeline_order = load_json(PIPELINE_ORDER_FILE)

@summary.route("/")
def display_summary():
    """Summary page."""
    selected_stages = session.get("stages", [])
    selected_level = session.get("security_level", "")
    selected_tools = session.get("tools", {})

    # Extract all pipeline stages from pipeline_order.json
    pipeline_stages = [item['stage'] for item in pipeline_order['pipeline']]

    # Filter out only the stages the user selected
    # and ensure each stage has the {"standard":[], "custom":[]} structure
    filtered_tools = {}
    for stage in pipeline_stages:
        if stage in selected_stages:
            # Retrieve the user's tool selection, defaulting to the two-field structure
            stage_tools = selected_tools.get(stage, {"standard": [], "custom": []})
            
            # Make sure stage_tools is a dict with both keys
            if not isinstance(stage_tools, dict):
                stage_tools = {"standard": [], "custom": []}
            if "standard" not in stage_tools:
                stage_tools["standard"] = []
            if "custom" not in stage_tools:
                stage_tools["custom"] = []

            filtered_tools[stage] = stage_tools

    # Build the final user response object
    user_responses = {
        "selected_level": selected_level,
        "stages": selected_stages,
        "tools": filtered_tools
    }

    # Save to user_responses.json
    with open(USER_RESPONSES_FILE, 'w') as f:
        json.dump(user_responses, f, indent=4)

    return render_template("summary.html", responses=user_responses)
