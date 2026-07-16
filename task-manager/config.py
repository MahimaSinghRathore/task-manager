"""
config.py
---------
Centralized application configuration.

Configuration values are pulled from environment variables (via a .env file)
so that secrets never live in source control. Three configuration profiles
are provided: Development, Testing, and Production.
"""

import os
from datetime import timedelta
from dotenv import load_dotenv
from sqlalchemy.engine import URL

# Load environment variables from a .env file if present.
basedir = os.path.abspath(os.path.dirname(__file__))
load_dotenv(os.path.join(basedir, ".env"))


class Config:
    """Base configuration with settings shared across all environments."""

    # --- Security ---------------------------------------------------------
    SECRET_KEY = os.environ.get("SECRET_KEY", "change-this-secret-key-in-production")
    WTF_CSRF_ENABLED = True
    WTF_CSRF_TIME_LIMIT = None  # Tokens do not expire mid-session

    # --- Database -----------------------------------------------------------
    DB_USER = os.environ.get("DB_USER", "root")
    DB_PASSWORD = os.environ.get("DB_PASSWORD", "password")
    DB_HOST = os.environ.get("DB_HOST", "localhost")
    DB_PORT = os.environ.get("DB_PORT", "3306")
    DB_NAME = os.environ.get("DB_NAME", "task_manager_db")

    SQLALCHEMY_DATABASE_URI = os.environ.get(
    "DATABASE_URL",
    URL.create(
        drivername="mysql+pymysql",
        username=DB_USER,
        password=DB_PASSWORD,
        host=DB_HOST,
        port=int(DB_PORT),
        database=DB_NAME,
    ),
)
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS = {
        "pool_pre_ping": True,   # Verify connections before using them
        "pool_recycle": 280,     # Recycle connections before MySQL times them out
    }

    # --- Sessions -------------------------------------------------------
    PERMANENT_SESSION_LIFETIME = timedelta(days=7)
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = "Lax"

    # --- Pagination -------------------------------------------------------
    TASKS_PER_PAGE = 8

    # --- Uploads (profile pictures, etc.) ----------------------------------
    UPLOAD_FOLDER = os.path.join(basedir, "static", "images", "uploads")
    MAX_CONTENT_LENGTH = 2 * 1024 * 1024  # 2 MB max upload size
    ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "gif"}


class DevelopmentConfig(Config):
    """Configuration used during local development."""

    DEBUG = True
    SESSION_COOKIE_SECURE = False


class TestingConfig(Config):
    """Configuration used when running automated tests."""

    TESTING = True
    DEBUG = True
    WTF_CSRF_ENABLED = False
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        "TEST_DATABASE_URL", "sqlite:///:memory:"
    )


class ProductionConfig(Config):
    """Configuration used in production deployments."""

    DEBUG = False
    SESSION_COOKIE_SECURE = True  # Requires HTTPS


# Maps the FLASK_ENV / FLASK_CONFIG value to the matching config class.
config = {
    "development": DevelopmentConfig,
    "testing": TestingConfig,
    "production": ProductionConfig,
    "default": DevelopmentConfig,
}
