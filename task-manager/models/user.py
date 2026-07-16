"""
models/user.py
---------------
User model: authentication credentials + profile information.
"""

from datetime import datetime
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

from models import db


class User(UserMixin, db.Model):
    """
    Represents an application user.

    UserMixin (from Flask-Login) supplies default implementations of
    `is_authenticated`, `is_active`, `is_anonymous`, and `get_id()`.
    """

    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False, index=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(256), nullable=False)

    # Optional profile fields (used by the Profile page feature).
    full_name = db.Column(db.String(120), nullable=True)
    bio = db.Column(db.String(255), nullable=True)
    avatar_filename = db.Column(db.String(255), nullable=True, default=None)

    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(
        db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False
    )

    # One-to-many relationship: a User has many Tasks.
    # `cascade="all, delete-orphan"` ensures a user's tasks are removed
    # if the user account is deleted.
    tasks = db.relationship(
        "Task",
        backref="owner",
        lazy="dynamic",
        cascade="all, delete-orphan",
    )

    # --- Password helpers ---------------------------------------------------
    def set_password(self, password):
        """Hash and store a plaintext password using Werkzeug's PBKDF2/SHA256."""
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        """Verify a plaintext password against the stored hash."""
        return check_password_hash(self.password_hash, password)

    # --- Convenience / stats -----------------------------------------------
    def task_counts(self):
        """
        Returns a dict summarizing this user's task counts, used to populate
        the dashboard summary cards.
        """
        from models.task import Task
        from datetime import date

        base = self.tasks
        return {
            "total": base.count(),
            "pending": base.filter_by(status="Pending").count(),
            "in_progress": base.filter_by(status="In Progress").count(),
            "completed": base.filter_by(status="Completed").count(),
            "overdue": base.filter(
                Task.due_date < date.today(), Task.status != "Completed"
            ).count(),
        }

    def __repr__(self):
        return f"<User {self.username}>"
