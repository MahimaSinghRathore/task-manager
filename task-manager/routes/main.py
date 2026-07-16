"""
routes/main.py
---------------
Main blueprint: public landing page and the authenticated dashboard.
"""

from datetime import date, timedelta
from flask import Blueprint, render_template, redirect, url_for
from flask_login import login_required, current_user

from models.task import Task

main_bp = Blueprint("main", __name__)


@main_bp.route("/")
def index():
    """Public landing page. Redirects logged-in users to the dashboard."""
    if current_user.is_authenticated:
        return redirect(url_for("main.dashboard"))
    return render_template("index.html")


@main_bp.route("/dashboard")
@login_required
def dashboard():
    """
    Authenticated dashboard: summary cards, recent tasks, and
    upcoming deadlines, all scoped to the current user.
    """
    counts = current_user.task_counts()

    recent_tasks = (
        current_user.tasks.order_by(Task.created_at.desc()).limit(5).all()
    )

    upcoming_cutoff = date.today() + timedelta(days=7)
    upcoming_deadlines = (
        current_user.tasks.filter(
            Task.due_date.isnot(None),
            Task.due_date >= date.today(),
            Task.due_date <= upcoming_cutoff,
            Task.status != "Completed",
        )
        .order_by(Task.due_date.asc())
        .limit(5)
        .all()
    )

    total = counts["total"] or 1  # avoid division by zero in the progress bar
    completion_percent = round((counts["completed"] / total) * 100)

    return render_template(
        "dashboard.html",
        counts=counts,
        recent_tasks=recent_tasks,
        upcoming_deadlines=upcoming_deadlines,
        completion_percent=completion_percent,
    )
