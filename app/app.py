from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from flask_session import Session
import os

db = SQLAlchemy()

def create_app():
    """
    Create the Flask application.

    This function is the application factory. It is the entry point
    for the Flask application. It is called by the WSGI server.

    The application is configured with the following settings:

        - SQLALCHEMY_DATABASE_URI: The URI of the database.
            If the environment variable DATABASE_URL is set, it is
            used. Otherwise, the URI is set to "sqlite:///feedback.db".
        - SQLALCHEMY_TRACK_MODIFICATIONS: If this is set to True, Flask-SQLAlchemy
            will track object modifications. This is disabled for performance reasons.
        - SESSION_TYPE: The type of session interface to use.
            This is set to 'filesystem' for file-based sessions.
    
    The application also registers the blueprint in routes_bp and
    initializes the database with the database models defined in models.
    Finally, CORS is enabled for all routes.
    
    Returns:
        The Flask application instance.
    """
    app = Flask(__name__)
    # app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL')
    app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///feedback.db"
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SESSION_TYPE'] = 'filesystem'
    Session(app)
    
    db.init_app(app)
    
    with app.app_context():
        from .routes_bp import routes_bp
        app.register_blueprint(routes_bp)
        db.create_all()
    CORS(app)
    return app