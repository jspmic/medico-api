from src.models.init import HOST, \
        api, app
from src.resources import Home


api.add_resource(Home, "/")
