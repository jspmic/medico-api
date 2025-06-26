from flask import jsonify, Response
from flask_restful import Resource, abort, request, marshal_with
from marshmallow import Schema, fields

from .models.models import app, db, Utilisateur
from .models.init import logger
from .functions import hash_password

from flask_jwt_extended import create_access_token
from flask_jwt_extended import get_jwt_identity
from flask_jwt_extended import jwt_required
from flask_jwt_extended import JWTManager

jwt = JWTManager(app)


# Schemas Definition

class UtilisateurPOSTSchema(Schema):
    nom = fields.Str(required=True)
    sexe = fields.Str(required=True)
    dateNaissance = fields.Date(required=True)
    email = fields.Email()
    numeroTelephone = fields.Str()
    province = fields.Str(required=True)
    commune = fields.Str(required=True)
    password = fields.Str(required=True)


class UtilisateurGETInputSchema(Schema):
    email = fields.Email()
    numeroTelephone = fields.Str()
    password = fields.Str(required=True)


class UtilisateurGETOutputSchema(Schema):  # Similar to UtilisateurPOST schema
    nom = fields.Str(required=True)
    sexe = fields.Str(required=True)
    dateNaissance = fields.Date(required=True)
    email = fields.Email()
    numeroTelephone = fields.Str()
    province = fields.Str(required=True)
    commune = fields.Str(required=True)
    password = fields.Str(required=True)
    access_token = fields.Str(required=True)


# Resources definition

class UtilisateurResource(Resource):
    def get(self):
        try:
            user = UtilisateurGETInputSchema().load(request.args)
        except Exception as e:
            logger.error(f"Error when loading user using GET schema %s: {e}",
                         "(GET /user)")
            abort(404, message="User not provided correctly")

        # Verifying if user provided email or numeroTelephone
        email = user.get("email", "")
        numeroTelephone = user.get("numeroTelephone", "")
        if email == "" and numeroTelephone == "":
            logger.warning(f"Nor 'email' nor 'numeroTelephone' was provided %s - provided user: {user}",
                           "(GET /user)")
            abort(404, message="No login info was provided")

        password = user.get("password")
        if not password:
            logger.warning(f"Password not provided %s - provided user: {user}",
                           "(GET /user)")
            abort(403, message="Password not provided")

        password = hash_password(password)

        existing_user_email: Utilisateur = Utilisateur.query.filter_by(email=email,
                                                                       password=password).first()
        existing_user_numeroTelephone: Utilisateur = Utilisateur.query.filter_by(
                numeroTelephone=numeroTelephone,
                password=password).first()

        if existing_user_email:
            access_token = create_access_token(identity=existing_user_email.get_identity(),
                                               expires_delta=None)
            logger.info(f"Generated access token: {access_token}")
            result = UtilisateurGETOutputSchema().dumps(
                    existing_user_email.to_dict(access_token))
            logger.info("User gave email and was granted access")
            return result, 200
        elif existing_user_numeroTelephone:
            access_token = create_access_token(
                    identity=existing_user_numeroTelephone.get_identity(),
                    expires_delta=None)
            logger.info(f"Generated access token: {access_token}")
            result = UtilisateurGETOutputSchema().dumps(
                    existing_user_numeroTelephone.to_dict(access_token))
            logger.info("User gave numeroTelephone and was granted access")
            return result, 200
        else:
            abort(403, message="Access denied")

    def post(self):
        try:
            user = UtilisateurPOSTSchema().load(request.json)
        except Exception as e:
            logger.error(f"Error when loading user using POST schema %s: {e}",
                         "(POST /user)")
            abort(404, message="User not provided correctly")

        email = user.get("email", "")
        numeroTelephone = user.get("numeroTelephone", "")

        if email == "" and numeroTelephone == "":
            logger.warning(f"Nor 'email' nor 'numeroTelephone' was provided %s - provided user: {user}",
                           "(POST /user)")
            abort(404, message="No contact info was provided")

        password = user.get("password")
        if len(password) != 64:
            logger.warning(f"Invalid password {password} - provided user %s: {user}",
                           "(POST /user)")
            abort(404, message="Invalid password format")

        # Checking if the given user doesn't exist

        existing_user = Utilisateur.query.filter_by(email=email).first()
        existing_user2 = Utilisateur.query.filter_by(
                numeroTelephone=numeroTelephone).first()

        if existing_user or existing_user2:
            logger.info(f"User already exists - provided user: {user}")
            abort(403, message="User already exists")

        # Adding new user
        new_user = Utilisateur(nom=user["nom"],
                               sexe=user["sexe"],
                               dateNaissance=user["dateNaissance"],
                               email=email,
                               numeroTelephone=numeroTelephone,
                               province=user["province"],
                               commune=user["commune"],
                               password=user["password"]
                               )
        db.session.add(new_user)
        db.session.commit()
        logger.info("Added user successfully")
        return {"message": "User created successfully"}, 201


class Test(Resource):
    @jwt_required()
    def get(self):
        username = get_jwt_identity()
        logger.info(f"User '{username}' is accessing a protected route")
        v = {"message": f"{username} connected"}
        return v, 200


class Home(Resource):
    def get(self):
        return {"message": "medico api"}
