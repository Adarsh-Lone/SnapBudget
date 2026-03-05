import os
from urllib.parse import quote_plus


class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY", "snapbudget-dev-key")

    DB_HOST = os.environ.get("DB_HOST", "localhost")
    DB_PORT = int(os.environ.get("DB_PORT", "3306"))
    DB_NAME = os.environ.get("DB_NAME", "snapbudget")
    DB_USER = os.environ.get("DB_USER", "root")

    # Raw password from env or default; will be URL-encoded for the URI
    _raw_password = os.environ.get("DB_PASSWORD", "Vishwakarma@2024")
    DB_PASSWORD = quote_plus(_raw_password)

    # MySQL connection
    SQLALCHEMY_DATABASE_URI = (
        f"mysql+mysqlconnector://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
    )

    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Optional override for Windows
    TESSERACT_CMD = os.environ.get("TESSERACT_CMD")


config = Config()