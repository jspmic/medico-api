from .init import app, logger
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase
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


class ServiceHopital(db.Model):
    __tablename__ = "service_hopital"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    service_id = db.Column(db.Integer, db.ForeignKey('service.id'))
    hopital_id = db.Column(db.Integer, db.ForeignKey('hopital.id'))


class Service(db.Model):
    __tablename__ = "service"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    nom = db.Column(db.String(60), unique=True, nullable=False)
    description = db.Column(db.String(254), nullable=True)
    service = db.relationship('Hopital', secondary=ServiceHopital.__table__,
                              back_populates='service')

    def to_dict(self):
        return {
                self.nom: self.description
                }


class Hopital(db.Model):
    __tablename__ = "hopital"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    nom = db.Column(db.String(100), unique=True, nullable=False)
    adresse = db.Column(db.String(100), nullable=True)
    service = db.relationship('Service', secondary=ServiceHopital.__table__,
                              back_populates='hopital')

    def to_dict(self):
        return {
                self.nom: self.adresse
                }
