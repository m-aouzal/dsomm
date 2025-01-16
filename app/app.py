from flask import Flask
from app.blueprints.home import home
from app.blueprints.levels import levels
from app.blueprints.stages import stages
from app.blueprints.tools import tools
from app.blueprints.summary import summary
from app.blueprints.conflict_resolution import conflict_resolution
def create_app():
    app = Flask(__name__)
    app.secret_key = 'your_secret_key_here'

    # Register blueprints
    app.register_blueprint(home)
    app.register_blueprint(levels, url_prefix='/levels')
    app.register_blueprint(stages, url_prefix='/stages')
    app.register_blueprint(tools, url_prefix='/tools')
    app.register_blueprint(summary, url_prefix='/summary')
    app.register_blueprint(conflict_resolution, url_prefix="/conflict-resolution")
    return app

if __name__ == "__main__":
    app = create_app()
    app.run(debug=True)
