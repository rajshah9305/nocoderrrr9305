# backend/__init__.py
from flask import Flask
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from flask_socketio import SocketIO
import os
from dotenv import load_dotenv

# Load environment variables from .env file for local development
load_dotenv()

# Initialize extensions
db = SQLAlchemy()
socketio = SocketIO(cors_allowed_origins="*")  # works for dev; restrict in prod

def create_app():
    app = Flask(__name__)
    # Config
    # Use os.getenv for environment variables with a fallback for dev
    app.config["SECRET_KEY"] = os.getenv("SECRET_KEY", "dev-secret")
    
    # Get the DATABASE_URL from environment variables for security
    # This will be provided by Netlify during deployment
    app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("DATABASE_URL")
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    # CORS: allow Vite dev server & your production domain
    CORS(app, resources={r"/api/*": {"origins": os.getenv("CORS_ORIGINS", "*")}})

    # DB init
    db.init_app(app)

    # Lazy-import routes so blueprints can register if they exist
    try:
        from .routes.api import api_bp
        app.register_blueprint(api_bp, url_prefix="/api")
    except Exception:
        # If routes not present yet, still run the app
        pass

    return app

def create_socketio_app():
    app = create_app()
    socketio.init_app(app)
    return app
