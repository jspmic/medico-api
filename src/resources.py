from flask import jsonify, Response
from flask_restful import Resource, abort, request, marshal_with, \
        HTTPException
from marshmallow import Schema, fields

from .models.models import app, db, Utilisateur, Hopital, \
        Service, service_hopital, RDV
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


class RDVGETOutputSchema(Schema):
    output = fields.List(
            fields.Dict(
                keys=fields.Str(),
                values=fields.Raw()
            )
        )


class RDVPOSTSchema(Schema):
    nom = fields.Str(required=True)
    sexe = fields.Str(required=True)
    contact = fields.Str()
    province = fields.Str()
    commune = fields.Str()
    dateTime = fields.DateTime(required=True)
    hopital = fields.Str(required=True)
    service = fields.Str(required=True)
    reference_id = fields.Integer()


class RDVPOST2Schema(Schema):
    nom = fields.Str(required=True)
    sexe = fields.Str(required=True)
    contact = fields.Str()
    dateTime = fields.DateTime(required=True)
    hopital = fields.Str(required=True)
    service = fields.Str(required=True)
    reference_id = fields.Integer()


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
            _service = _service.strip()
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


class RDVs(Resource):
    @retry(
        retry=retry_if_not_exception_type((HTTPException)),
        wait=wait_exponential(multiplier=1, min=2, max=5),
        stop=stop_after_attempt(3)
    )
    def get(self):
        id_user = request.args.get("id_user", "")
        if id_user == "":
            return {"message": "Invalid request"}, 404
        id_user = int(id_user)
        user = Utilisateur.query.filter_by(id=id_user).first()
        rdv_for_user: list[RDV] = user.rdv
        response: list[dict] = []
        for _rdv in rdv_for_user:
            response.append(_rdv.to_dict())

        json_response = RDVGETOutputSchema().dumps({"output": response})
        return json_response, 200

    @retry(
        retry=retry_if_not_exception_type((HTTPException)),
        wait=wait_exponential(multiplier=1, min=2, max=5),
        stop=stop_after_attempt(3)
    )
    def post(self):
        try:
            rdv = RDVPOSTSchema().load(request.json)
        except Exception as e:
            logger.error(
                    f"Error when loading rdv using first POST schema %s: {e}",
                    "(POST /rdv)")

        try:
            logger.info("Attempting to use second POST schema for RDV")
            rdv = RDVPOST2Schema().load(request.json)
        except Exception as e:
            logger.error(
                    f"Error when loading rdv using second POST schema %s: {e}",
                    "(POST /rdv)")
            return {"message": "Invalid request"}, 404

        contact = rdv.get("contact", None)
        province = rdv.get("province", None)
        commune = rdv.get("commune", None)
        _rdv = RDV(nom=rdv['nom'],
                   sexe=rdv['sexe'],
                   contact=contact,
                   province=province,
                   commune=commune,
                   dateTime=rdv['dateTime'],
                   )
        db.session.add(_rdv)

        # Searching for the corresponding Hospital
        _hopital = rdv['hopital']
        hospital = Hopital.query.filter_by(
                nom=_hopital).first()
        if not hospital:
            logger.error(f"Hopital {_hopital} not found in DB - POST /rdv")
            return {"message": f"Hopital {_hopital} not found"}, 404

        # Searching for the corresponding Service
        _service = rdv['service']
        service = Service.query.filter_by(
                nom=_service).first()
        if not service:
            logger.error(f"Service {_service} not found in DB - POST /rdv")
            return {"message": f"Service {_service} not found"}, 404

        # Searching for the corresponding Utilisateur
        _userID = rdv['reference_id']
        user = Utilisateur.query.filter_by(
                id=_userID).first()
        if not user:
            logger.error(f"User of id {_userID} not found in DB - POST /rdv")
            return {"message": f"User {_userID} not found"}, 404

        db.session.commit()  # Writing the changes to add the RDV
        _rdv.reference = user
        _rdv.hopital = hospital
        _rdv.service = service

        db.session.commit()  # Writing the changes to the foreign keys
        logger.info(f"Inserted RDV successfully {_rdv.to_dict()}")

        return {"message": "Inserted successfully"}, 201


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
