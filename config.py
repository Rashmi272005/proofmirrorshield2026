import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))

class Config:
    SECRET_KEY = os.environ.get(
        "SECRET_KEY",
        "proofmirror-development-key-change-before-deployment"
    )

    DATABASE_PATH = os.path.join(
        BASE_DIR,
        "database",
        "proofmirror.db"
    )

    JSON_SORT_KEYS = False
    MAX_CONTENT_LENGTH = 2 * 1024 * 1024  # 2 MB