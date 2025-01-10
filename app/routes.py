from flask import Blueprint, render_template, request, session, redirect, url_for
import json

main = Blueprint('main', __name__)

# Load data
def load_json(file_path):
    with open(file_path, 'r') as file:
        return json.load(file)

PIPELINE_ORDER_FILE = "./data/pipeline_order.json"
QUESTIONS_FILE = "./data/questions.json"
USER_RESPONSES_FILE = "./data/user_responses.json"

pipeline_order = load_json(PIPELINE_ORDER_FILE)
questions_data = load_json(QUESTIONS_FILE)

@main.route("/")
def home():
    """Homepage."""
    return render_template("home.html")

@main.route("/levels", methods=["GET", "POST"])
def levels():
    """Page to select security level."""
    if request.method == "POST":
        session['security_level'] = request.form.get('security_level')
        return redirect(url_for('main.stages'))

    level_question = questions_data['sections'][1]['questions'][0]
    return render_template("level.html", question=level_question)

@main.route("/stages", methods=["GET", "POST"])
def stages():
    """Page to select pipeline stages."""
    if request.method == "POST":
        session['stages'] = request.form.getlist('stages')
        return redirect(url_for('main.tools'))

    stages_question = questions_data['sections'][2]['questions'][0]
    return render_template("stages.html", question=stages_question, pipeline_order=pipeline_order)

@main.route("/tools", methods=["GET", "POST"])
def tools():
    """Page to select tools for each stage."""
    if request.method == "POST":
        selected_tools = session.get("tools", {})
        stage = session['current_stage']
        selected_tools[stage] = request.form.getlist('tools')
        session['tools'] = selected_tools

        # Move to the next stage
        stages = session.get('stages', [])
        current_index = stages.index(stage) + 1
        if current_index < len(stages):
            session['current_stage'] = stages[current_index]
            return redirect(url_for('main.tools'))
        else:
            return redirect(url_for('main.summary'))

    stages = session.get('stages', [])
    if not stages:
        return redirect(url_for('main.stages'))

    # Get the current stage
    if 'current_stage' not in session:
        session['current_stage'] = stages[0]

    current_stage = session['current_stage']
    tools = next((item['tools'] for item in pipeline_order['pipeline'] if item['stage'] == current_stage), [])

    return render_template("tools.html", stage=current_stage, tools=tools)

@main.route("/summary")
def summary():
    """Summary page."""
    selected_stages = session.get("stages", [])
    selected_level = session.get("security_level", "")
    selected_tools = session.get("tools", {})

    user_responses = {
        "stages": selected_stages,
        "selected_level": selected_level,
        "tools": selected_tools
    }

    # Save responses to JSON
    with open(USER_RESPONSES_FILE, 'w') as f:
        json.dump(user_responses, f, indent=4)

    return render_template("summary.html", responses=user_responses)
