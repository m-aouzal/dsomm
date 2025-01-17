from flask import Flask, render_template, redirect, url_for, request
from app.blueprints.home import home
from app.blueprints.levels import levels
from app.blueprints.stages import stages
from app.blueprints.tools import tools
from app.blueprints.summary import summary
from app.blueprints.conflict_resolution import conflict_resolution

# Créer l'instance Flask
app = Flask(__name__)

# Données des niveaux (à adapter selon vos besoins)
stages_by_level = {
    'levels': {
        '1': {'label': 'Basic Security'},
        '2': {'label': 'Intermediate Security'},
        '3': {'label': 'Advanced Security'}
    }
}

# Question initiale
question = {
    'text': 'Choose your security implementation level:'
}

# Vos routes
@app.route('/')
def home():
    return render_template('home.html')

@app.route('/start')
def start():
    return redirect(url_for('level'))

@app.route('/level/', methods=['GET', 'POST'])
def level():
    try:
        if request.method == 'POST':
            selected_level = request.form.get('security_level')
            # Ici, vous pouvez ajouter la logique pour gérer le niveau sélectionné
            return redirect(url_for('some_next_page'))  # Remplacez 'some_next_page' par votre prochaine route
        
        return render_template('level.html', 
                             stages_by_level=stages_by_level,
                             question=question)
    except Exception as e:
        app.logger.error(f"Error in level route: {str(e)}")
        return render_template('error.html'), 500

# Si vous avez d'autres routes, ajoutez-les ici

if __name__ == '__main__':
    app.run(debug=True)
