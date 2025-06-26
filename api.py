from src.models.init import HOST, \
        api, app
from src.resources import Home, UtilisateurResource, \
        Test
from src.models.models import db


api.add_resource(Home, "/")
api.add_resource(UtilisateurResource, "/user")
api.add_resource(Test, "/test")
