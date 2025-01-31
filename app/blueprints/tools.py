from flask import Blueprint, render_template, request, session, redirect, url_for
import json

tools = Blueprint('tools', __name__)

PIPELINE_ORDER_FILE = "./data/pipeline_order.json"
CUSTOM_TOOLS_FILE = "./data/custom_tools.json"

def load_json(file_path):
    # For now, always return {} for custom_tools
    if file_path == CUSTOM_TOOLS_FILE:
        return {}
    try:
        with open(file_path, 'r') as file:
            return json.load(file)
    except FileNotFoundError:
        return {}

def save_json(file_path, data):
    with open(file_path, 'w') as file:
        json.dump(data, file, indent=4)

pipeline_order = load_json(PIPELINE_ORDER_FILE)



@tools.route("/", methods=["GET", "POST"])
def select_tools():
    """Step-by-step selection of tools for each stage."""
    stages = session.get("stages", [])
    if not stages:
        # If no stages in session, redirect to stage selection
        return redirect(url_for("stages.select_stages"))
    
    # Use an index (current_stage_index) to iterate through the stages
    if "current_stage_index" not in session:
        session["current_stage_index"] = 0

    current_stage_index = session["current_stage_index"]

    # When all stages have been processed, redirect to conflict resolution
    if current_stage_index >= len(stages):
        return redirect(url_for("conflict_resolution.resolve_conflict"))

    current_stage = stages[current_stage_index]

    # Load or initialize selected_tools from session
    selected_tools = session.get("tools")
    if not isinstance(selected_tools, dict):
        selected_tools = {}

    # Ensure the current stage in selected_tools has the correct structure
    if current_stage not in selected_tools:
        selected_tools[current_stage] = {"standard": [], "custom": []}

    # Load custom_tools (forced to {})
    custom_tools = load_json(CUSTOM_TOOLS_FILE)

    if request.method == "POST":
        # Process form submission
        chosen_tools = request.form.getlist("tools")
        if "none" in chosen_tools:
            # If "none" is chosen, overwrite with {"standard": ["none"], "custom": []}
            selected_tools[current_stage] = {"standard": ["none"], "custom": []}
        else:
            # Otherwise update the "standard" list
            selected_tools[current_stage]["standard"] = chosen_tools

        # Process custom tools
        custom_tool_names = request.form.getlist('custom_tool')
        for tool_name in custom_tool_names:
            tool_name = tool_name.strip()
            if tool_name:
                # Insert into custom_tools for the stage
                if current_stage not in custom_tools:
                    custom_tools[current_stage] = []
                if tool_name not in custom_tools[current_stage]:
                    custom_tools[current_stage].append(tool_name)

                # Add to the "custom" list for the current stage
                if tool_name not in selected_tools[current_stage]["custom"]:
                    selected_tools[current_stage]["custom"].append(tool_name)

        # Update session and save custom_tools file
        session["tools"] = selected_tools
        save_json(CUSTOM_TOOLS_FILE, custom_tools)

        # Move to the next stage
        session["current_stage_index"] = current_stage_index + 1

        # Redirect to conflict resolution if we've processed all stages
        if session["current_stage_index"] >= len(stages):
            return redirect(url_for("conflict_resolution.resolve_conflict"))
        else:
            return redirect(url_for("tools.select_tools"))

    # --- GET request: Show the form for the current stage ---
    # Retrieve default tools for current stage from pipeline_order
    default_tools = []
    for item in pipeline_order.get("pipeline", []):
        if item["stage"] == current_stage:
            default_tools = item.get("tools", [])
            break

    # Retrieve any custom tools for this stage
    available_custom_tools = custom_tools.get(current_stage, [])

    # Combine and deduplicate the two lists
    all_tools = list(set(default_tools + available_custom_tools))
    all_tools.sort()
    if "none" not in all_tools:
        all_tools.append("none")

    return render_template("tools.html", stage=current_stage, tools=all_tools)
