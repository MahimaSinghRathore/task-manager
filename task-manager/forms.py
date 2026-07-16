"""
forms.py
--------
WTForms form classes used across the app. Centralizing them here keeps
validation logic out of the route handlers and templates.
"""

from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import (
    StringField,
    PasswordField,
    TextAreaField,
    SelectField,
    DateField,
    BooleanField,
    SubmitField,
)
from wtforms.validators import (
    DataRequired,
    Email,
    Length,
    EqualTo,
    Optional,
    ValidationError,
)

from models.user import User
from models.task import PRIORITY_CHOICES, STATUS_CHOICES, CATEGORY_CHOICES


class RegistrationForm(FlaskForm):
    """Sign-up form with uniqueness validation for username/email."""

    username = StringField(
        "Username",
        validators=[DataRequired(), Length(min=3, max=64)],
    )
    email = StringField(
        "Email",
        validators=[DataRequired(), Email(), Length(max=120)],
    )
    password = PasswordField(
        "Password",
        validators=[DataRequired(), Length(min=8, message="Password must be at least 8 characters.")],
    )
    confirm_password = PasswordField(
        "Confirm Password",
        validators=[DataRequired(), EqualTo("password", message="Passwords must match.")],
    )
    submit = SubmitField("Create Account")

    def validate_username(self, field):
        if User.query.filter_by(username=field.data.strip()).first():
            raise ValidationError("That username is already taken.")

    def validate_email(self, field):
        if User.query.filter_by(email=field.data.lower().strip()).first():
            raise ValidationError("An account with that email already exists.")


class LoginForm(FlaskForm):
    """Login form. Accepts a username or email in the same field."""

    identifier = StringField("Username or Email", validators=[DataRequired()])
    password = PasswordField("Password", validators=[DataRequired()])
    remember_me = BooleanField("Remember Me")
    submit = SubmitField("Log In")


class TaskForm(FlaskForm):
    """Create / edit form for a Task."""

    title = StringField("Title", validators=[DataRequired(), Length(max=150)])
    description = TextAreaField("Description", validators=[Optional(), Length(max=2000)])
    category = SelectField(
        "Category", choices=[(c, c) for c in CATEGORY_CHOICES], validators=[DataRequired()]
    )
    priority = SelectField(
        "Priority", choices=[(p, p) for p in PRIORITY_CHOICES], validators=[DataRequired()]
    )
    status = SelectField(
        "Status", choices=[(s, s) for s in STATUS_CHOICES], validators=[DataRequired()]
    )
    due_date = DateField("Due Date", validators=[Optional()], format="%Y-%m-%d")
    submit = SubmitField("Save Task")


class EditProfileForm(FlaskForm):
    """Edit profile form. Validates uniqueness excluding the current user."""

    full_name = StringField("Full Name", validators=[Optional(), Length(max=120)])
    username = StringField("Username", validators=[DataRequired(), Length(min=3, max=64)])
    email = StringField("Email", validators=[DataRequired(), Email(), Length(max=120)])
    bio = TextAreaField("Bio", validators=[Optional(), Length(max=255)])
    avatar = FileField(
        "Profile Picture", validators=[Optional(), FileAllowed(["jpg", "jpeg", "png", "gif"], "Images only!")]
    )
    submit = SubmitField("Save Changes")

    def __init__(self, current_user, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._current_user = current_user

    def validate_username(self, field):
        user = User.query.filter_by(username=field.data.strip()).first()
        if user and user.id != self._current_user.id:
            raise ValidationError("That username is already taken.")

    def validate_email(self, field):
        user = User.query.filter_by(email=field.data.lower().strip()).first()
        if user and user.id != self._current_user.id:
            raise ValidationError("An account with that email already exists.")


class ChangePasswordForm(FlaskForm):
    """Change password form: requires the current password for verification."""

    current_password = PasswordField("Current Password", validators=[DataRequired()])
    new_password = PasswordField(
        "New Password",
        validators=[DataRequired(), Length(min=8, message="Password must be at least 8 characters.")],
    )
    confirm_new_password = PasswordField(
        "Confirm New Password",
        validators=[DataRequired(), EqualTo("new_password", message="Passwords must match.")],
    )
    submit = SubmitField("Change Password")
