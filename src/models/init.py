import os
from flask_restful import Api
from dotenv import find_dotenv, load_dotenv
from flask import Flask

find_dotenv("../../.env")
load_dotenv()

HOST = os.getenv("HOST")
USER = os.getenv("USERNAME")
PASSWORD = os.getenv("PASSWORD")
DB_NAME = os.getenv("DB_NAME")


app = Flask(__name__)
api = Api(app)

try:
    app.config["SQLALCHEMY_DATABASE_URI"] = \
            f"mysql://{USER}:{PASSWORD}@{HOST}/{DB_NAME}"
except Exception:
    pass
