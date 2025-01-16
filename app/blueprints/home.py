from flask import Blueprint, render_template, redirect, url_for, session
import json

home = Blueprint('home', __name__)

USER_RESPONSES_FILE = "./data/user_responses.json"

@home.route("/")
def home_page():
    """Page d'accueil."""
    return render_template("home.html")

@home.route("/start")
def start():
    """Initialise le fichier user_responses.json et redirige vers la sélection de niveau."""
    initial_data = {
        "selected_level": "",
        "stages": [],
        "tools": {}
    }
    # Réinitialiser le fichier user_responses.json
    with open(USER_RESPONSES_FILE, 'w') as f:
        json.dump(initial_data, f, indent=4)
    
    # Vider la session pour repartir d'un état vierge
    session.clear()
    
    # Rediriger vers la page de sélection de niveau (par exemple: levels.select_level)
    return redirect(url_for('levels.select_level'))
