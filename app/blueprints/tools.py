from flask import Blueprint, render_template, request, session, redirect, url_for
import json

tools = Blueprint('tools', __name__)

PIPELINE_ORDER_FILE = "./data/pipeline_order.json"
CUSTOM_TOOLS_FILE = "./data/custom_tools.json"

# Load data
def load_json(file_path):
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
    stages = session.get('stages', [])
    if not stages:
        return redirect(url_for('stages.select_stages'))

    custom_tools = load_json(CUSTOM_TOOLS_FILE)

    if request.method == "POST":
        selected_tools = session.get("tools", {})
        current_stage = session.get('current_stage')

        if current_stage:
            chosen_tools = request.form.getlist('tools')
            if "none" in chosen_tools:
                selected_tools[current_stage] = ["none"]
            else:
                selected_tools[current_stage] = chosen_tools

            custom_tool_names = request.form.getlist('custom_tool')
            for custom_tool_name in custom_tool_names:
                if custom_tool_name and custom_tool_name.strip():
                    custom_tool_name = custom_tool_name.strip()

                    if not isinstance(custom_tools, dict):
                        custom_tools = {}

                    if current_stage not in custom_tools:
                        custom_tools[current_stage] = []

                    if custom_tool_name not in custom_tools[current_stage]:
                        custom_tools[current_stage].append(custom_tool_name)

                    if custom_tool_name not in selected_tools[current_stage]:
                        selected_tools[current_stage].append(custom_tool_name)

            save_json(CUSTOM_TOOLS_FILE, custom_tools)
            session['tools'] = selected_tools

            current_index = stages.index(current_stage)
            if current_index + 1 < len(stages):
                session['current_stage'] = stages[current_index + 1]
                return redirect(url_for('tools.select_tools'))
            else:
                return redirect(url_for('summary.display_summary'))

    if 'current_stage' not in session or session['current_stage'] not in stages:
        session['current_stage'] = stages[0]

    current_stage = session['current_stage']

    if current_stage not in stages:
        session.pop('current_stage', None)
        return redirect(url_for('stages.select_stages'))

    default_tools = next(
        (item['tools'] for item in pipeline_order['pipeline'] if item['stage'] == current_stage), []
    )

    available_custom_tools = []
    for stage in stages:
        if stage in custom_tools:
            available_custom_tools.extend(custom_tools[stage])
        if stage == current_stage:
            break

    all_tools = list(set(default_tools + available_custom_tools))
    all_tools.sort()
    if "none" not in all_tools:
        all_tools.append("none")

    return render_template("tools.html", stage=current_stage, tools=all_tools)
