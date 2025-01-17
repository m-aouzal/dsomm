from flask import Flask
from app.blueprints.home import home
import os

app = Flask(__name__, 
    static_folder='app/static',  # Spécifiez le dossier static
    template_folder='app/templates'  # Spécifiez le dossier templates
)

app.secret_key = 'votre_clé_secrète_ici'
app.register_blueprint(home)

if __name__ == '__main__':
    app.run(debug=True)
