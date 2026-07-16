"""
routes/tasks.py
----------------
Tasks blueprint: full CRUD, search, filtering, sorting, and pagination.
Every query is scoped to `current_user` so users can never see or modify
another user's tasks.
"""

from flask import Blueprint, render_template, redirect, url_for, flash, request, abort, jsonify
from flask_login import login_required, current_user

from models import db
from models.task import Task, PRIORITY_CHOICES, STATUS_CHOICES, CATEGORY_CHOICES
from forms import TaskForm

tasks_bp = Blueprint("tasks", __name__)


def _get_owned_task_or_404(task_id):
    """Fetches a task by id, ensuring it belongs to the current user."""
    task = Task.query.get_or_404(task_id)
    if task.user_id != current_user.id:
        abort(403)
    return task


@tasks_bp.route("/")
@login_required
def list_tasks():
    """
    Lists the current user's tasks with search, filtering, sorting,
    and pagination applied.
    """
    query = current_user.tasks

    # --- Search --------------------------------------------------------
    search_term = request.args.get("q", "").strip()
    if search_term:
        query = query.filter(Task.title.ilike(f"%{search_term}%"))

    # --- Filters -------------------------------------------------------
    status_filter = request.args.get("status", "")
    if status_filter in STATUS_CHOICES:
        query = query.filter(Task.status == status_filter)

    priority_filter = request.args.get("priority", "")
    if priority_filter in PRIORITY_CHOICES:
        query = query.filter(Task.priority == priority_filter)

    category_filter = request.args.get("category", "")
    if category_filter in CATEGORY_CHOICES:
        query = query.filter(Task.category == category_filter)

    # --- Sorting -------------------------------------------------------
    sort_by = request.args.get("sort", "due_date_asc")
    priority_rank = {"High": 0, "Medium": 1, "Low": 2}

    # MySQL-compatible sorting
    sort_map = {
        "due_date_asc": Task.due_date.asc(),
        "due_date_desc": Task.due_date.desc(),
        "created_desc": Task.created_at.desc(),
        "title_asc": Task.title.asc(),
    }

    if sort_by == "priority":
        tasks_list = query.all()
        tasks_list.sort(key=lambda t: priority_rank.get(t.priority, 3))

        page = request.args.get("page", 1, type=int)
        per_page = 8
        start = (page - 1) * per_page
        paginated_items = tasks_list[start:start + per_page]
        total = len(tasks_list)

        class _SimplePagination:
            """Simple pagination object compatible with templates."""

            def __init__(self, items, page, per_page, total):
                self.items = items
                self.page = page
                self.per_page = per_page
                self.total = total
                self.pages = max(1, (total + per_page - 1) // per_page)
                self.has_prev = page > 1
                self.has_next = page < self.pages
                self.prev_num = page - 1
                self.next_num = page + 1

            def iter_pages(self):
                return range(1, self.pages + 1)

        pagination = _SimplePagination(
            paginated_items,
            page,
            per_page,
            total
        )

    else:
        query = query.order_by(
            sort_map.get(sort_by, sort_map["due_date_asc"])
        )

        page = request.args.get("page", 1, type=int)
        pagination = query.paginate(
            page=page,
            per_page=8,
            error_out=False
        )

    return render_template(
        "tasks/list.html",
        pagination=pagination,
        tasks=pagination.items,
        search_term=search_term,
        status_filter=status_filter,
        priority_filter=priority_filter,
        category_filter=category_filter,
        sort_by=sort_by,
        status_choices=STATUS_CHOICES,
        priority_choices=PRIORITY_CHOICES,
        category_choices=CATEGORY_CHOICES,
    )


@tasks_bp.route("/new", methods=["GET", "POST"])
@login_required
def create_task():
    """Creates a new task for the current user."""
    form = TaskForm()

    if form.validate_on_submit():
        task = Task(
            user_id=current_user.id,
            title=form.title.data.strip(),
            description=form.description.data,
            category=form.category.data,
            priority=form.priority.data,
            status=form.status.data,
            due_date=form.due_date.data,
        )

        db.session.add(task)
        db.session.commit()

        flash("Task created successfully.", "success")
        return redirect(url_for("tasks.list_tasks"))

    return render_template(
        "tasks/form.html",
        form=form,
        title="New Task"
    )


@tasks_bp.route("/<int:task_id>")
@login_required
def view_task(task_id):
    """Displays the full detail view of a single task."""
    task = _get_owned_task_or_404(task_id)
    return render_template("tasks/view.html", task=task)


@tasks_bp.route("/<int:task_id>/edit", methods=["GET", "POST"])
@login_required
def edit_task(task_id):
    """Edits an existing task."""
    task = _get_owned_task_or_404(task_id)
    form = TaskForm(obj=task)

    if form.validate_on_submit():
        form.populate_obj(task)

        if task.status == "Completed" and not task.completed_at:
            task.mark_completed()

        db.session.commit()

        flash("Task updated successfully.", "success")
        return redirect(url_for("tasks.view_task", task_id=task.id))

    return render_template(
        "tasks/form.html",
        form=form,
        title="Edit Task",
        task=task
    )


@tasks_bp.route("/<int:task_id>/delete", methods=["POST"])
@login_required
def delete_task(task_id):
    """Deletes a task."""
    task = _get_owned_task_or_404(task_id)

    db.session.delete(task)
    db.session.commit()

    flash("Task deleted.", "info")
    return redirect(url_for("tasks.list_tasks"))


@tasks_bp.route("/<int:task_id>/toggle-status", methods=["POST"])
@login_required
def toggle_status(task_id):
    """
    AJAX endpoint used by the dashboard/task list to quickly mark a task
    as Completed or reopen it.
    """
    task = _get_owned_task_or_404(task_id)

    if task.status == "Completed":
        task.status = "Pending"
        task.completed_at = None
    else:
        task.mark_completed()

    db.session.commit()

    return jsonify(
        success=True,
        status=task.status
    )