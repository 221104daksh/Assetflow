import os
from dotenv import load_dotenv

basedir = os.path.abspath(os.path.dirname(__file__))
load_dotenv(os.path.join(basedir, ".env"))


class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY", "dev-secret-key-change-me")

    # DATABASE_URL is the single knob to switch SQLite -> PostgreSQL.
    # e.g. postgresql://user:pass@host:5432/assetflow
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        "DATABASE_URL", "sqlite:///" + os.path.join(basedir, "instance", "assetflow.db")
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    PUBLIC_BASE_URL = os.environ.get("PUBLIC_BASE_URL", "http://localhost:5000")

    WTF_CSRF_ENABLED = True
    CACHE_TYPE = "SimpleCache"
    CACHE_DEFAULT_TIMEOUT = 60

    REMEMBER_COOKIE_DURATION = 60 * 60 * 24 * 14  # 14 days

    # Upload settings for org logo
    UPLOAD_FOLDER = os.path.join(basedir, "assetflow", "static", "images", "uploads")
    MAX_CONTENT_LENGTH = 4 * 1024 * 1024  # 4MB
