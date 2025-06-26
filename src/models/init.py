import os
from flask_restful import Api
from dotenv import find_dotenv, load_dotenv
from flask import Flask
from datetime import timedelta
import logging

find_dotenv("../../.env")
load_dotenv()

# Constants definition

HOST = os.getenv("HOST")
USER = os.getenv("USERNAME")
PASSWORD = os.getenv("PASSWORD")
DB_NAME = os.getenv("DB_NAME")
SECRET_KEY = os.getenv("SECRET_KEY")
EXPIRES = timedelta(minutes=8)

# Logging setup

logger = logging.getLogger(__name__)
logging.basicConfig(filename="log.log", encoding="utf-8",
                    datefmt="%Y/%m/%d %H-%M-%S",
                    format="%(levelname)s:%(asctime)s:%(message)s",
                    level=logging.DEBUG)

# App setup

app = Flask(__name__)
api = Api(app)

app.config["SQLALCHEMY_DATABASE_URI"] = \
        f"mysql+mysqldb://{USER}:{PASSWORD}@{HOST}/{DB_NAME}"
app.config["JWT_SECRET_KEY"] = SECRET_KEY
app.config["JWT_ACCESS_TOKEN_EXPIRES"] = EXPIRES
