"""
models/task.py
---------------
Task model: represents a single to-do item belonging to a User.
"""

from datetime import datetime, date
from models import db


# Allowed values, centralized here so templates/forms/routes all stay in sync.
PRIORITY_CHOICES = ["Low", "Medium", "High"]
STATUS_CHOICES = ["Pending", "In Progress", "Completed"]
CATEGORY_CHOICES = ["Work", "Personal", "Study", "Health", "Finance", "Other"]


class Task(db.Model):
    """Represents a single task/to-do item owned by a User."""

    __tablename__ = "tasks"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False, index=True)

    title = db.Column(db.String(150), nullable=False)
    description = db.Column(db.Text, nullable=True)
    category = db.Column(db.String(50), nullable=False, default="Other")
    priority = db.Column(db.String(20), nullable=False, default="Medium")
    status = db.Column(db.String(20), nullable=False, default="Pending", index=True)

    due_date = db.Column(db.Date, nullable=True, index=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(
        db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False
    )
    completed_at = db.Column(db.DateTime, nullable=True)

    # --- Computed / display helpers -----------------------------------------
    @property
    def is_overdue(self):
        """True if the task has a due date in the past and isn't completed."""
        if not self.due_date or self.status == "Completed":
            return False
        return self.due_date < date.today()

    @property
    def days_until_due(self):
        """Signed day count until the due date (negative if overdue)."""
        if not self.due_date:
            return None
        return (self.due_date - date.today()).days

    @property
    def priority_badge_class(self):
        """Bootstrap color class per priority level, used in templates."""
        return {"Low": "success", "Medium": "warning", "High": "danger"}.get(
            self.priority, "secondary"
        )

    @property
    def status_badge_class(self):
        """Bootstrap color class per status, used in templates."""
        return {
            "Pending": "secondary",
            "In Progress": "info",
            "Completed": "success",
        }.get(self.status, "secondary")

    def mark_completed(self):
        """Flags a task as completed and stamps the completion time."""
        self.status = "Completed"
        self.completed_at = datetime.utcnow()

    def to_dict(self):
        """Serializes the task, e.g. for JSON/AJAX responses."""
        return {
            "id": self.id,
            "title": self.title,
            "description": self.description,
            "category": self.category,
            "priority": self.priority,
            "status": self.status,
            "due_date": self.due_date.isoformat() if self.due_date else None,
            "created_at": self.created_at.isoformat(),
            "is_overdue": self.is_overdue,
        }

    def __repr__(self):
        return f"<Task {self.id}: {self.title!r}>"
