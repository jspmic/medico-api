from flask_restful import Resource, marshal_with
from marshmallow import Schema, fields


# Schemas Definition

class UtilisateurSchema(Schema):
    nom = fields.Str()
    dateNaissance = fields.Date()
    email = fields.Email()
    numeroTelephone = fields.Str()
    province = fields.Str()
    commune = fields.Str()


# Resources definition

class UtilisateurResource(Resource):
    def get(self):
        pass

    @marshal_with(UtilisateurSchema)
    def post(self, admin_code: int):
        pass


class Home(Resource):
    def get(self):
        return {"message": "medico api"}
