from flask import Blueprint, render_template, request, session, redirect, url_for
import json

levels = Blueprint('levels', __name__)

# Load data
def load_json(file_path):
    with open(file_path, 'r') as file:
        return json.load(file)

STAGES_BY_LEVEL_FILE = "./data/stages_by_level.json"
QUESTIONS_FILE = "./data/questions.json"

stages_by_level = load_json(STAGES_BY_LEVEL_FILE)
questions_data = load_json(QUESTIONS_FILE)

@levels.route("/", methods=["GET", "POST"])
def select_level():
    """Page to select security level."""
    if request.method == "POST":
        selected_level = request.form.get('security_level')
        if not selected_level:
            return redirect(url_for('levels.select_level'))
        session['security_level'] = selected_level
        return redirect(url_for('stages.select_stages'))

    level_question = questions_data['sections'][1]['questions'][0]
    return render_template("level.html", question=level_question, stages_by_level=stages_by_level)
