"""
app.py
------
Application entry point.

Uses the Flask "application factory" pattern so the app can be configured
differently for development, testing, and production, and so that
Blueprints / extensions can be registered cleanly without circular imports.
"""

import os
from flask import Flask, render_template
from flask_wtf import CSRFProtect

from config import config
from models import db, login_manager


csrf = CSRFProtect()


def create_app(config_name=None):
    """
    Application factory.

    Args:
        config_name (str): One of "development", "testing", "production".
            Defaults to the FLASK_CONFIG environment variable, or
            "development" if unset.

    Returns:
        Flask: A fully configured Flask application instance.
    """
    config_name = config_name or os.environ.get("FLASK_CONFIG", "development")

    app = Flask(__name__, instance_relative_config=True)
    app.config.from_object(config[config_name])

    # Ensure instance / upload folders exist.
    os.makedirs(app.instance_path, exist_ok=True)
    os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)

    # --- Initialize extensions ------------------------------------------
    db.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = "auth.login"
    login_manager.login_message = "Please log in to access this page."
    login_manager.login_message_category = "warning"
    csrf.init_app(app)

    # --- Register Blueprints ---------------------------------------------
    from routes.auth import auth_bp
    from routes.main import main_bp
    from routes.tasks import tasks_bp
    from routes.profile import profile_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(main_bp)
    app.register_blueprint(tasks_bp, url_prefix="/tasks")
    app.register_blueprint(profile_bp, url_prefix="/profile")

    # --- Error handlers ----------------------------------------------------
    @app.errorhandler(404)
    def not_found_error(error):
        return render_template("errors/404.html"), 404

    @app.errorhandler(403)
    def forbidden_error(error):
        return render_template("errors/403.html"), 403

    @app.errorhandler(500)
    def internal_error(error):
        db.session.rollback()
        return render_template("errors/500.html"), 500

    # --- Template context processors ---------------------------------------
    @app.context_processor
    def inject_globals():
        from datetime import datetime
        return {"current_year": datetime.utcnow().year}

    # --- CLI commands -------------------------------------------------------
    @app.cli.command("init-db")
    def init_db():
        """Create all database tables (flask init-db)."""
        db.create_all()
        print("Database tables created successfully.")

    @app.cli.command("drop-db")
    def drop_db():
        """Drop all database tables (flask drop-db)."""
        db.drop_all()
        print("Database tables dropped.")

    return app


# Allows `flask run` (via FLASK_APP=app.py) and `python app.py` to both work.
app = create_app()


if __name__ == "__main__":
    app.run(debug=app.config.get("DEBUG", True))
