from flask import jsonify, Response
from flask_restful import Resource, abort, request, marshal_with, \
        HTTPException
from marshmallow import Schema, fields

from .models.models import app, db, Utilisateur, Hopital, \
        Service, service_hopital
from .models.init import logger
from .functions import hash_password

from tenacity import retry, wait_exponential, \
        stop_after_attempt, retry_if_not_exception_type

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
    id = fields.Integer(required=True)
    nom = fields.Str(required=True)
    sexe = fields.Str(required=True)
    dateNaissance = fields.Date(required=True)
    email = fields.Email()
    numeroTelephone = fields.Str()
    province = fields.Str(required=True)
    commune = fields.Str(required=True)
    password = fields.Str(required=True)
    access_token = fields.Str(required=True)
    services = fields.Dict(keys=fields.Str(), values=fields.Str())


class HopitalPOSTSchema(Schema):
    nom = fields.Str(required=True)
    adresse = fields.Str()
    services = fields.List(fields.Str())


class HopitalGETOutputSchema(Schema):
    hopitaux = fields.Dict(keys=fields.Str(),
                           values=fields.List(fields.Str()))


# Resources definition

class UtilisateurResource(Resource):
    @retry(
        retry=retry_if_not_exception_type((HTTPException)),
        wait=wait_exponential(multiplier=1, min=2, max=5),
        stop=stop_after_attempt(3)
    )
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

        query_services: list[Service] = Service.query.all()
        services: dict = {}
        if query_services:
            for service in query_services:
                services.update(service.to_dict())

        if existing_user_email:
            access_token = create_access_token(identity=existing_user_email.get_identity(),
                                               expires_delta=None)
            logger.info(f"Generated access token: {access_token}")
            _result = existing_user_email.to_dict(access_token)
            _result['services'] = services
            result = UtilisateurGETOutputSchema().dumps(_result)
            logger.info("User gave email and was granted access")
            return result, 200
        elif existing_user_numeroTelephone:
            access_token = create_access_token(
                    identity=existing_user_numeroTelephone.get_identity(),
                    expires_delta=None)
            logger.info(f"Generated access token: {access_token}")
            _result = existing_user_numeroTelephone.to_dict(access_token)
            _result['services'] = services
            result = UtilisateurGETOutputSchema().dumps(_result)
            logger.info("User gave numeroTelephone and was granted access")
            return result, 200
        else:
            abort(403, message="Access denied")

    @retry(
        retry=retry_if_not_exception_type((HTTPException)),
        wait=wait_exponential(multiplier=1, min=2, max=5),
        stop=stop_after_attempt(3)
    )
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


class Hopitals(Resource):

    @retry(
        retry=retry_if_not_exception_type((HTTPException)),
        wait=wait_exponential(multiplier=1, min=2, max=5),
        stop=stop_after_attempt(3)
    )
    def get(self):
        hopitaux: list[Hopital] = db.session.query(Hopital).all()
        hopitaux_services = {}
        for hopital in hopitaux:
            _services: list[Service] = hopital.services
            services: list[str] = list(map(
                lambda x: x.nom.capitalize(), _services))
            hopitaux_services.update({hopital.nom: services})
        logger.debug(hopitaux_services)
        dumped = HopitalGETOutputSchema().dump({"hopitaux": hopitaux_services})
        return dumped, 200

    @retry(
        retry=retry_if_not_exception_type((HTTPException)),
        wait=wait_exponential(multiplier=1, min=2, max=5),
        stop=stop_after_attempt(3)
    )
    def post(self):
        try:
            hopital = HopitalPOSTSchema().load(request.json)
        except Exception as e:
            logger.error(
                    f"Error when loading hopital using POST schema %s: {e}",
                    "(POST /hopital)")
            abort(404, message="Hopital not provided correctly")

        logger.info(hopital)
        adresse = hopital.get('adresse', None)
        try:
            new_hopital = Hopital(nom=hopital['nom'],
                                  adresse=adresse)
            db.session.add(new_hopital)
            db.session.commit()
        except Exception as e:
            logger.error(f"Could not add hopital '{hopital}': {e}")
            return {"message": "Invalid request"}, 404

        services: list[str] = hopital['services']
        for _service in services:
            service: Service
            try:
                service = db.session.execute(db.select(Service).filter_by(
                    nom=_service.lower())).scalar_one()
            except Exception:
                logger.warning(f"No service '{_service}' found in DB")
                service = Service(nom=_service.lower())
                db.session.add(service)
                db.session.commit()
                logger.info(f"Added new service '{_service}'")

            new_hopital.services.append(service)
            logger.info(f"Added service {service} to hopital {new_hopital}")

        db.session.commit()
        logger.info(f"Added hopital '{new_hopital.to_dict()}' successfully")
        return {"message": "Hopital inserted successfully"}, 201


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
