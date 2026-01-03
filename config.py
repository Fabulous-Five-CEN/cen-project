import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))

class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY", "dev_secret_key")
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        "SQLALCHEMY_DATABASE_URI",
        os.environ.get(
            "DATABASE_URL",
            f"sqlite:///{os.path.join(BASE_DIR, 'instance', 'database.sqlite3')}",
        ),
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    DEMO_MODE = os.environ.get("APP_ENV") == "demo"
