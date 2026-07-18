# TaskFlow — Task Management Web Application

A production-quality, full-stack task management app built with **Flask** and **MySQL**, featuring secure authentication, a live dashboard, full task CRUD, search/filter/sort, and a modern glassmorphism UI with dark mode.

![Status](https://img.shields.io/badge/status-active-success) ![Python](https://img.shields.io/badge/python-3.10%2B-blue) ![License](https://img.shields.io/badge/license-MIT-lightgrey)

---

## ✨ Features

### Authentication
- Registration, login, logout with hashed passwords (Werkzeug PBKDF2)
- Session management via Flask-Login, protected routes
- Duplicate username/email validation, flash-message feedback

### Dashboard
- Summary cards: Total, Pending, In Progress, Completed, Overdue
- Overall completion progress bar
- Recent tasks and upcoming deadlines (next 7 days)

### Task Management
- Full CRUD: create, view, edit, delete
- Fields: title, description, category, priority, status, due date, created date
- One-click status toggle (AJAX, no page reload)
- Deadline countdown on the task detail page

### Search & Filters
- Search by title
- Filter by status, priority, category
- Sort by due date (asc/desc), priority (High → Low), newest, title
- Pagination on the task list

### UI / UX
- Glassmorphism cards over an animated gradient background
- Sidebar navigation + responsive top navbar
- Dark / light mode toggle (persisted via `localStorage`)
- Bootstrap 5 + Bootstrap Icons, smooth hover/entry animations
- Toast notifications, loading spinner, empty-state illustrations
- Fully responsive (mobile sidebar, responsive tables)

### Profile
- View profile with task statistics and completion rate
- Edit profile (name, username, email, bio, avatar upload)
- Change password (requires current password)

### Security
- Passwords hashed, never stored in plaintext
- CSRF protection on all forms (Flask-WTF)
- Login-required decorators on every protected route
- Ownership checks on every task route (403 if not the task's owner)
- SQLAlchemy ORM (parameterized queries) prevents SQL injection
- Jinja2 auto-escaping prevents XSS

---

## 🛠 Technologies

**Backend:** Python, Flask, Flask-SQLAlchemy, Flask-Login, Flask-WTF, Flask-Migrate, Werkzeug
**Frontend:** HTML5, CSS3, Bootstrap 5, Vanilla JavaScript, Bootstrap Icons
**Database:** MySQL (via PyMySQL)

---

## 🚀 Installation

### Prerequisites
- Python 3.10+
- MySQL Server 8.0+
- pip / virtualenv

### 1. Clone and set up a virtual environment
```bash
git clone <your-repo-url> task-manager
cd task-manager
python3 -m venv venv
source venv/bin/activate      # Windows: venv\Scripts\activate
```

### 2. Install dependencies
```bash
pip install -r requirements.txt
```

### 3. Configure environment variables
Create a `.env` file in the project root:
```env
SECRET_KEY=your-super-secret-key
FLASK_CONFIG=development

DB_USER=root
DB_PASSWORD=your-mysql-password
DB_HOST=localhost
DB_PORT=3306
DB_NAME=task_manager_db
```

### 4. Set up the database
Create the database in MySQL:
```sql
CREATE DATABASE task_manager_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```

Then initialize the tables:
```bash
export FLASK_APP=app.py     # Windows: set FLASK_APP=app.py
flask init-db
```

### 5. Run the application
```bash
flask run
```
Visit **http://127.0.0.1:5000** in your browser.

---

## 📁 Project Structure

```
task-manager/
│
├── app.py                  # Application factory, blueprint registration
├── config.py                # Environment-based configuration
├── forms.py                  # WTForms form classes
├── requirements.txt
├── README.md
│
├── models/
│   ├── __init__.py           # db + login_manager setup
│   ├── user.py                # User model
│   └── task.py                # Task model
│
├── routes/
│   ├── __init__.py
│   ├── auth.py                 # Register / login / logout
│   ├── main.py                 # Landing page + dashboard
│   ├── tasks.py                 # Task CRUD, search/filter/sort
│   └── profile.py               # Profile view/edit, change password
│
├── static/
│   ├── css/style.css            # Theme, glassmorphism, layout, responsive
│   ├── js/main.js                # Theme toggle, toasts, AJAX, spinner
│   └── images/uploads/           # User-uploaded avatars
│
├── templates/
    ├── base.html
    ├── index.html
    ├── dashboard.html
    ├── auth/                      # register.html, login.html
    ├── tasks/                      # list.html, form.html, view.html
    ├── profile/                     # view.html, edit.html, change_password.html
    ├── errors/                       # 404.html, 403.html, 500.html
    └── partials/                      # _flash.html, _empty_state.html

```

---

## 🔮 Future Improvements

- Task attachments (file uploads per task)
- Team workspaces / shared task boards
- Email notifications for approaching deadlines
- Recurring tasks
- Kanban drag-and-drop board view
- REST API + OpenAPI docs for third-party integrations
- Two-factor authentication

---

## 📄 License

This project is licensed under the MIT License — see the `LICENSE` file for details.
