from flask import Blueprint, render_template, request, session, redirect, url_for
import json

main = Blueprint('main', __name__)

# Load data
def load_json(file_path):
    with open(file_path, 'r') as file:
        return json.load(file)
    
    
STAGES_BY_LEVEL_FILE = "./data/stages_by_level.json"
PIPELINE_ORDER_FILE = "./data/pipeline_order.json"
QUESTIONS_FILE = "./data/questions.json"
USER_RESPONSES_FILE = "./data/user_responses.json"

stages_by_level = load_json(STAGES_BY_LEVEL_FILE)
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
        selected_level = request.form.get('security_level')
        if not selected_level:
            print("No security level selected. Redirecting to levels.")
            return redirect(url_for('main.levels'))

        # Store the numeric level in the session
        session['security_level'] = selected_level
        print(f"Selected security level: Level {selected_level}")
        return redirect(url_for('main.stages'))

    # Render the level selection page
    level_question = questions_data['sections'][1]['questions'][0]
    return render_template("level.html", question=level_question, stages_by_level=stages_by_level)


@main.route("/stages", methods=["GET", "POST"])
def stages():
    """Page to select pipeline stages."""
    selected_level = session.get('security_level')
    if not selected_level:
        print("No security level found in session. Redirecting to levels.")
        return redirect(url_for('main.levels'))

    print(f"Security level in session: {selected_level}")

    # Directly use the numeric key to fetch stages
    level_key = selected_level  # Already stored as numeric in session
    if level_key not in stages_by_level['levels']:
        print(f"No stages found for level: {selected_level}. Redirecting to levels.")
        return redirect(url_for('main.levels'))

    # Fetch stages relevant to the selected level
    level_stages = stages_by_level['levels'][level_key].get('stages', [])
    print(f"Stages for Level {level_key}: {level_stages}")

    # Save the filtered stages in the session
    session['filtered_stages'] = level_stages

    if request.method == "POST":
        session['stages'] = request.form.getlist('stages')
        print(f"Selected stages: {session['stages']}")
        return redirect(url_for('main.tools'))

    stages_question = questions_data['sections'][2]['questions'][0]
    return render_template("stages.html", question=stages_question, stages=level_stages)


@main.route("/tools", methods=["GET", "POST"])
def tools():
    """Page to select tools for each stage."""
    # Get the selected stages
    stages = session.get('stages', [])
    if not stages:
        print("No stages found in session. Redirecting to stages.")
        return redirect(url_for('main.stages'))

    # Handle POST request (save selected tools)
    if request.method == "POST":
        selected_tools = session.get("tools", {})
        current_stage = session.get('current_stage')

        # Save tools for the current stage
        if current_stage:
            selected_tools[current_stage] = request.form.getlist('tools')
            session['tools'] = selected_tools

            # Move to the next stage in the selected stages list
            current_index = stages.index(current_stage)
            if current_index + 1 < len(stages):
                session['current_stage'] = stages[current_index + 1]
                print(f"Moving to next stage: {session['current_stage']}")
            else:
                print("All stages completed. Redirecting to summary.")
                return redirect(url_for('main.summary'))

    # Handle GET request
    if 'current_stage' not in session or session['current_stage'] not in stages:
        session['current_stage'] = stages[0]

    current_stage = session['current_stage']

    # Validate the current stage
    if current_stage not in stages:
        print(f"Current stage '{current_stage}' not in selected stages. Redirecting to stages.")
        session.pop('current_stage', None)
        return redirect(url_for('main.stages'))

    # Fetch tools for the current stage
    tools = next(
        (item['tools'] for item in pipeline_order['pipeline'] if item['stage'] == current_stage), []
    )

    print(f"Current stage: {current_stage}, Available tools: {tools}")
    return render_template("tools.html", stage=current_stage, tools=tools)


@main.route("/summary")
def summary():
    """Summary page."""
    selected_stages = session.get("stages", [])
    selected_level = session.get("security_level", "")
    selected_tools = session.get("tools", {})

    # Get the order of stages from the pipeline
    pipeline_stages = [item['stage'] for item in pipeline_order['pipeline']]

    # Filter and sort tools based on the order in the pipeline
    filtered_tools = {
        stage: selected_tools.get(stage, [])
        for stage in pipeline_stages
        if stage in selected_stages
    }

    # Create the user responses object
    user_responses = {
        "selected_level": selected_level,
        "stages": selected_stages,
        "tools": filtered_tools
    }

    # Save the responses to the JSON file
    with open(USER_RESPONSES_FILE, 'w') as f:
        json.dump(user_responses, f, indent=4)

    # Debugging output for validation
    print("Summary responses:", user_responses)

    return render_template("summary.html", responses=user_responses)
