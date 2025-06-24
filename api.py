from src.models.init import HOST, \
        api, app
from src.resources import Home
from src.models.models import db


api.add_resource(Home, "/")
