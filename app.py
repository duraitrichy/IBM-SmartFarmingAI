"""
app.py — Flask application factory and entry point for SmartFarmingAI.
"""

import os
from flask import Flask
from flask_session import Session
from loguru import logger
from config import ActiveConfig
from database import init_db


def create_app(config=None) -> Flask:
    """Application factory."""
    app = Flask(__name__)
    app.config.from_object(config or ActiveConfig)
    app.config["UPLOAD_FOLDER"] = ActiveConfig.UPLOAD_FOLDER
    app.config["MAX_CONTENT_LENGTH"] = ActiveConfig.MAX_CONTENT_LENGTH

    # Session
    app.config["SESSION_TYPE"] = "filesystem"
    app.config["SESSION_FILE_DIR"] = "./.flask_session"
    Session(app)

    # Database
    init_db(app)

    # Register blueprints
    from routes import register_routes
    register_routes(app)

    # Ensure upload / report dirs exist
    os.makedirs(ActiveConfig.UPLOAD_FOLDER, exist_ok=True)
    os.makedirs(ActiveConfig.REPORTS_FOLDER, exist_ok=True)

    logger.info("SmartFarmingAI application created successfully.")
    return app


app = create_app()

if __name__ == "__main__":
    app.run(
        host="0.0.0.0",
        port=ActiveConfig.PORT,
        debug=ActiveConfig.DEBUG,
    )
