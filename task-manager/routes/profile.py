"""
routes/profile.py
------------------
Profile blueprint: view profile, edit profile details (with optional
avatar upload), and change password.
"""

import os
import uuid
from flask import Blueprint, render_template, redirect, url_for, flash, current_app
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename

from models import db
from forms import EditProfileForm, ChangePasswordForm

profile_bp = Blueprint("profile", __name__)


def _allowed_file(filename):
    ext = filename.rsplit(".", 1)[-1].lower() if "." in filename else ""
    return ext in current_app.config["ALLOWED_EXTENSIONS"]


@profile_bp.route("/")
@login_required
def view_profile():
    """Displays the current user's profile page with task statistics."""
    counts = current_user.task_counts()
    return render_template("profile/view.html", counts=counts)


@profile_bp.route("/edit", methods=["GET", "POST"])
@login_required
def edit_profile():
    """Edits profile fields (name, username, email, bio) and avatar."""
    form = EditProfileForm(current_user, obj=current_user)

    if form.validate_on_submit():
        current_user.full_name = form.full_name.data.strip() if form.full_name.data else None
        current_user.username = form.username.data.strip()
        current_user.email = form.email.data.lower().strip()
        current_user.bio = form.bio.data

        file = form.avatar.data
        if file and file.filename and _allowed_file(file.filename):
            ext = file.filename.rsplit(".", 1)[-1].lower()
            filename = secure_filename(f"user_{current_user.id}_{uuid.uuid4().hex}.{ext}")
            filepath = os.path.join(current_app.config["UPLOAD_FOLDER"], filename)
            file.save(filepath)
            current_user.avatar_filename = filename

        db.session.commit()
        flash("Profile updated successfully.", "success")
        return redirect(url_for("profile.view_profile"))

    return render_template("profile/edit.html", form=form)


@profile_bp.route("/change-password", methods=["GET", "POST"])
@login_required
def change_password():
    """Allows the current user to change their password."""
    form = ChangePasswordForm()

    if form.validate_on_submit():
        if not current_user.check_password(form.current_password.data):
            flash("Current password is incorrect.", "danger")
        else:
            current_user.set_password(form.new_password.data)
            db.session.commit()
            flash("Password changed successfully.", "success")
            return redirect(url_for("profile.view_profile"))

    return render_template("profile/change_password.html", form=form)
