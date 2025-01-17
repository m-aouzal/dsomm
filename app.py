from flask import Flask
from app.blueprints.home import home

app = Flask(__name__)
app.secret_key = 'votre_clé_secrète_ici'  # Nécessaire pour la session

# Enregistrement du blueprint
app.register_blueprint(home)

if __name__ == '__main__':
    app.run(debug=True)


