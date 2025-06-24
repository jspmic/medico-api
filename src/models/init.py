import os
from flask_restful import Api
from dotenv import find_dotenv, load_dotenv
from flask import Flask
import logging

find_dotenv("../../.env")
load_dotenv()

# Constants definition

HOST = os.getenv("HOST")
USER = os.getenv("USERNAME")
PASSWORD = os.getenv("PASSWORD")
DB_NAME = os.getenv("DB_NAME")

# Logging setup

logger = logging.getLogger(__name__)
logging.basicConfig("log.log", encoding="utf-8", level=logging.DEBUG)

# App setup

app = Flask(__name__)
api = Api(app)

try:
    app.config["SQLALCHEMY_DATABASE_URI"] = \
            f"mysql://{USER}:{PASSWORD}@{HOST}/{DB_NAME}"
    logger.info("Connected to database")
except Exception as e:
    logger.error(f"Encountered error when connecting to database: {e}")
    raise e
