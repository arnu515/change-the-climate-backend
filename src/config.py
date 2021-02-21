from os import getenv as env

SQLALCHEMY_DATABASE_URI = env("SQLALCHEMY_DATABASE_URI") or "sqlite:///../db.db"
SQLALCHEMY_TRACK_MODIFICATIONS = False
SECRET = env("SECRET") or "secret"
