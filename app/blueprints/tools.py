from flask import Blueprint, render_template, request, session, redirect, url_for
import json

tools = Blueprint('tools', __name__)

PIPELINE_ORDER_FILE = "./data/pipeline_order.json"

# Load data
def load_json(file_path):
    with open(file_path, 'r') as file:
        return json.load(file)

pipeline_order = load_json(PIPELINE_ORDER_FILE)

@tools.route("/", methods=["GET", "POST"])
def select_tools():
    """Page to select tools for each stage."""
    stages = session.get('stages', [])
    if not stages:
        return redirect(url_for('stages.select_stages'))

    if request.method == "POST":
        selected_tools = session.get("tools", {})
        current_stage = session.get('current_stage')
        if current_stage:
            chosen_tools = request.form.getlist('tools')
            if "none" in chosen_tools:
                selected_tools[current_stage] = ["none"]
            else:
                selected_tools[current_stage] = chosen_tools
            session['tools'] = selected_tools

            current_index = stages.index(current_stage)
            if current_index + 1 < len(stages):
                session['current_stage'] = stages[current_index + 1]
            else:
                return redirect(url_for('summary.display_summary'))

    if 'current_stage' not in session or session['current_stage'] not in stages:
        session['current_stage'] = stages[0]

    current_stage = session['current_stage']
    tools = next(
        (item['tools'] for item in pipeline_order['pipeline'] if item['stage'] == current_stage), []
    )
    tools.append("none")
    return render_template("tools.html", stage=current_stage, tools=tools)
