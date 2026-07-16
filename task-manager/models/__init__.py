"""
models/__init__.py
-------------------
Initializes the shared SQLAlchemy `db` instance and Flask-Login's
`login_manager`. Kept here (rather than in app.py) so that model modules
can import `db` without causing circular imports with the app factory.
"""

from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager

db = SQLAlchemy()
login_manager = LoginManager()


@login_manager.user_loader
def load_user(user_id):
    """
    Flask-Login calls this on every request to reload the user object
    from the user ID stored in the session.
    """
    from models.user import User
    return db.session.get(User, int(user_id))


# Import models so that they are registered with SQLAlchemy's metadata
# (important for `db.create_all()` / Flask-Migrate autogeneration).
from models.user import User   # noqa: E402, F401
from models.task import Task   # noqa: E402, F401
