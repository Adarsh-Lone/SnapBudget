import os
from urllib.parse import quote_plus

from dotenv import load_dotenv

# Load variables from a local .env file if present so you don't have to hardcode
# secrets like DB passwords in source control.
load_dotenv()


class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY", "snapbudget-dev-key")

    DB_HOST = os.environ.get("DB_HOST", "localhost")
    DB_PORT = int(os.environ.get("DB_PORT", "3306"))
    DB_NAME = os.environ.get("DB_NAME", "snapbudget")
    DB_USER = os.environ.get("DB_USER", "root")

    # NOTE: Do NOT hardcode real passwords here. Set DB_PASSWORD in your
    # environment or in a local .env file instead.
    _raw_password = os.environ.get("DB_PASSWORD", "Vedant@17")
    DB_PASSWORD = quote_plus(_raw_password) if _raw_password else ""

    # Optional full DATABASE_URL-style override, e.g.:
    # mysql+mysqlconnector://user:pass@host:3306/dbname
    _db_url_override = os.environ.get("DATABASE_URL")

    if _db_url_override:
        # Explicit database URL wins.
        SQLALCHEMY_DATABASE_URI = _db_url_override
    elif _raw_password:
        # If a password is provided, assume MySQL.
        SQLALCHEMY_DATABASE_URI = (
            f"mysql+mysqlconnector://{DB_USER}:{DB_PASSWORD}"
            f"@{DB_HOST}:{DB_PORT}/{DB_NAME}"
        )
    else:
        # Fallback: local SQLite DB so the app works out-of-the-box without
        # needing MySQL credentials configured.
        base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
        SQLALCHEMY_DATABASE_URI = f"sqlite:///{os.path.join(base_dir, 'snapbudget.db')}"

    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Optional override for Windows
    TESSERACT_CMD = os.environ.get("TESSERACT_CMD")


config = Config()