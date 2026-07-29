import os
from dotenv import load_dotenv

# --------------------------------------------------
# Base Directory
# --------------------------------------------------
basedir = os.path.abspath(os.path.dirname(__file__))

# Load .env for local development
load_dotenv(os.path.join(basedir, ".env"))

# --------------------------------------------------
# Database Configuration
# --------------------------------------------------
database_url = os.environ.get(
    "DATABASE_URL",
    "sqlite:///" + os.path.join(basedir, "instance", "assetflow.db"),
)

# --------------------------------------------------
# PostgreSQL Compatibility
# SQLAlchemy 2.x + psycopg (v3)
# --------------------------------------------------
if database_url.startswith("postgres://"):
    database_url = database_url.replace(
        "postgres://",
        "postgresql+psycopg://",
        1,
    )

elif database_url.startswith("postgresql://"):
    database_url = database_url.replace(
        "postgresql://",
        "postgresql+psycopg://",
        1,
    )

# --------------------------------------------------
# Configuration Class
# --------------------------------------------------
class Config:
    # Security
    SECRET_KEY = os.environ.get(
        "SECRET_KEY",
        "dev-secret-key-change-me",
    )

    # Database
    SQLALCHEMY_DATABASE_URI = database_url
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Public URL
    PUBLIC_BASE_URL = os.environ.get(
        "PUBLIC_BASE_URL",
        "http://localhost:5000",
    )

    # CSRF
    WTF_CSRF_ENABLED = True

    # Cache
    CACHE_TYPE = "SimpleCache"
    CACHE_DEFAULT_TIMEOUT = 60

    # Login
    REMEMBER_COOKIE_DURATION = 60 * 60 * 24 * 14  # 14 Days

    # Uploads
    UPLOAD_FOLDER = os.path.join(
        basedir,
        "assetflow",
        "static",
        "images",
        "uploads",
    )

    MAX_CONTENT_LENGTH = 4 * 1024 * 1024  # 4 MB