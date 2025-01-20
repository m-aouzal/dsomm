from flask import Flask

def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'your_secret_key'

    from .routes import main # type: ignore
    app.register_blueprint(main)

    from .blueprints.summary import summary
    app.register_blueprint(summary)

    return app
