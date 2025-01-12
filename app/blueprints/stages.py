from flask import Blueprint, render_template, request, session, redirect, url_for
import json

stages = Blueprint('stages', __name__)

STAGES_BY_LEVEL_FILE = "./data/stages_by_level.json"
QUESTIONS_FILE = "./data/questions.json"

# Load data
def load_json(file_path):
    with open(file_path, 'r') as file:
        return json.load(file)

stages_by_level = load_json(STAGES_BY_LEVEL_FILE)
questions_data = load_json(QUESTIONS_FILE)

@stages.route("/", methods=["GET", "POST"])
def select_stages():
    """Page to select pipeline stages."""
    selected_level = session.get('security_level')
    if not selected_level:
        return redirect(url_for('levels.select_level'))

    level_key = selected_level
    level_stages = stages_by_level['levels'].get(level_key, {}).get('stages', [])
    session['filtered_stages'] = level_stages

    if request.method == "POST":
        session['stages'] = request.form.getlist('stages')
        return redirect(url_for('tools.select_tools'))

    stages_question = questions_data['sections'][2]['questions'][0]
    return render_template("stages.html", question=stages_question, stages=level_stages)
