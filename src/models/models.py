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
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    nom = db.Column(db.String(254), nullable=False)
    dateNaissance = db.Column(db.Date, nullable=False)
    sexe = db.Column(db.String(1), nullable=False)
    email = db.Column(db.String(254), nullable=True)
    numeroTelephone = db.Column(db.String(254), nullable=True)
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
