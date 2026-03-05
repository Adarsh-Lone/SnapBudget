import os
from urllib.parse import quote_plus

class Config:
    SECRET_KEY = "snapbudget-dev-key"

    DB_HOST = "localhost"
    DB_PORT = 3306
    DB_NAME = "snapbudget"
    DB_USER = "root"

    _raw_password = "Vedant@17"
    DB_PASSWORD = quote_plus(_raw_password)

    SQLALCHEMY_DATABASE_URI = (
        f"mysql+mysqlconnector://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
    )

    SQLALCHEMY_TRACK_MODIFICATIONS = False

config = Config()