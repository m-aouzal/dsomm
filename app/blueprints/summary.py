from flask import Blueprint, render_template, session
import json

summary = Blueprint('summary', __name__)

USER_RESPONSES_FILE = "./data/user_responses.json"
PIPELINE_ORDER_FILE = "./data/pipeline_order.json"

# Load data
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

    pipeline_stages = [item['stage'] for item in pipeline_order['pipeline']]

    filtered_tools = {
        stage: selected_tools.get(stage, [])
        for stage in pipeline_stages
        if stage in selected_stages
    }

    user_responses = {
        "selected_level": selected_level,
        "stages": selected_stages,
        "tools": filtered_tools
    }

    with open(USER_RESPONSES_FILE, 'w') as f:
        json.dump(user_responses, f, indent=4)

    return render_template("summary.html", responses=user_responses)
