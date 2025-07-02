from src.models.init import HOST, \
        api, app
from src.resources import Home, UtilisateurResource, \
        Test, Hopitals, RDVs
from src.models.models import db


api.add_resource(Home, "/")
api.add_resource(UtilisateurResource, "/user")
api.add_resource(Test, "/test")
api.add_resource(Hopitals, "/hopital")
api.add_resource(RDVs, "/rdv")
