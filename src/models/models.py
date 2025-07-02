from .init import app, logger
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase
from datetime import datetime
from flask_migrate import Migrate


class Base(DeclarativeBase):
    pass


try:
    db = SQLAlchemy(app, model_class=Base)
    logger.info("Connected to database")
    migrate = Migrate(app, db)
    logger.info("Applied migrations...")
except Exception as e:
    logger.error(f"Error encountered when connecting to database: {e}")
    raise e


class Utilisateur(db.Model):
    __tablename__ = "utilisateur"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    nom = db.Column(db.String(254), nullable=False)
    dateNaissance = db.Column(db.Date, nullable=False)
    sexe = db.Column(db.String(1), nullable=False)
    email = db.Column(db.String(254), nullable=True, unique=True)
    numeroTelephone = db.Column(db.String(254), nullable=True, unique=True)
    province = db.Column(db.String(254), nullable=False)
    commune = db.Column(db.String(254), nullable=False)
    password = db.Column(db.String(65), nullable=False)
    rdv = db.relationship('RDV',
                          backref='reference')

    def get_identity(self):
        return self.nom

    def to_dict(self, access_token: str = ""):
        return {
                "id": self.id,
                "nom": self.nom,
                "sexe": self.sexe,
                "dateNaissance": self.dateNaissance,
                "email": self.email,
                "numeroTelephone": self.numeroTelephone,
                "province": self.province,
                "commune": self.commune,
                "password": self.password,
                "access_token": access_token
                }


service_hopital = db.Table('service_hopital',
                           db.Column('service_id',
                                     db.Integer, db.ForeignKey('service.id')),
                           db.Column('hopital_id',
                                     db.Integer, db.ForeignKey('hopital.id'))
                           )


class Service(db.Model):
    __tablename__ = "service"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    nom = db.Column(db.String(60), unique=True, nullable=False)
    description = db.Column(db.String(254), nullable=True)
    rdv = db.relationship('RDV', backref='service')

    def to_dict(self):
        return {
                self.nom: self.description
                }


class Hopital(db.Model):
    __tablename__ = "hopital"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    nom = db.Column(db.String(100), unique=True, nullable=False)
    adresse = db.Column(db.String(100), nullable=True)
    services = db.relationship('Service', secondary=service_hopital,
                               backref='hopitaux'
                               )
    rdv = db.relationship('RDV', backref='hopital')

    def to_dict(self):
        return {
                self.nom: self.adresse
                }


utilisateur_rdv = db.Table('utilisateur_service_hopital',
                           db.Column('utilisateur_id',
                                     db.Integer,
                                     db.ForeignKey(
                                         'utilisateur.id'
                                         )),
                           db.Column('rdv_id',
                                     db.Integer,
                                     db.ForeignKey(
                                         'rdv.id'
                                         )),
                           )


class RDV(db.Model):
    __tablename__ = "rdv"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    nom = db.Column(db.String(254), nullable=False)
    sexe = db.Column(db.String(1), nullable=False)
    province = db.Column(db.String(254), nullable=True)
    commune = db.Column(db.String(254), nullable=True)
    contact = db.Column(db.String(254), nullable=True)
    dateTime = db.Column(db.DateTime, nullable=False)
    hopital_id = db.Column(db.Integer, db.ForeignKey('hopital.id'))
    service_id = db.Column(db.Integer, db.ForeignKey('service.id'))
    utilisateur_id = db.Column(db.Integer, db.ForeignKey('utilisateur.id'))

    def to_dict(self):
        format = "%Y-%m-%d %H:%M:%S"
        return {
                "id": self.id,
                "nom": self.nom,
                "sexe": self.sexe,
                "contact": self.contact,
                "province": self.province,
                "commune": self.commune,
                "dateTime": datetime.strftime(self.dateTime, format),
                "hopital": self.hopital.nom,
                "reference_id": self.reference.id,
                "service": self.service.nom
                }
