from flask import Blueprint, render_template, session
import json
from .utils import (
    prepare_activities_for_gap_analysis,
    get_activities_for_level,
    apply_standard_tool_selection,
    apply_custom_tool_selection
)

summary = Blueprint('summary', __name__)

USER_RESPONSES_FILE = "./data/user_responses.json"
PIPELINE_ORDER_FILE = "./data/pipeline_order.json"

def load_json(file_path):
    with open(file_path, 'r') as file:
        return json.load(file)

def save_json(file_path, data):
    with open(file_path, 'w') as file:
        json.dump(data, file, indent=4, ensure_ascii=False)

pipeline_order = load_json(PIPELINE_ORDER_FILE)

@summary.route("/")
def display_summary():
    """Summary page."""
    # Load existing user responses to preserve activities
    existing_responses = load_json(USER_RESPONSES_FILE)
    
    selected_stages = session.get("stages", [])
    selected_level = session.get("security_level", "")
    selected_tools = session.get("tools", {})

    # Extract all pipeline stages from pipeline_order.json
    pipeline_stages = [item['stage'] for item in pipeline_order['pipeline']]

    # Filter out only the stages the user selected
    filtered_tools = {}
    for stage in pipeline_stages:
        if stage in selected_stages:
            stage_tools = selected_tools.get(stage, {"standard": [], "custom": []})
            
            if not isinstance(stage_tools, dict):
                stage_tools = {"standard": [], "custom": []}
            if "standard" not in stage_tools:
                stage_tools["standard"] = []
            if "custom" not in stage_tools:
                stage_tools["custom"] = []

            filtered_tools[stage] = stage_tools

    # Build the final user response object, preserving activities
    user_responses = {
        "selected_level": selected_level,
        "stages": selected_stages,
        "tools": filtered_tools,
        "activities": existing_responses.get("activities", [])  # Preserve existing activities
    }

    # Save to user_responses.json
    save_json(USER_RESPONSES_FILE, user_responses)

    return render_template("summary.html", responses=user_responses)
