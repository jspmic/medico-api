from .init import app
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase
from flask_migrate import Migrate


class Base(DeclarativeBase):
    pass


db = SQLAlchemy(app, model_class=Base)
migrate = Migrate(app, db)


class Utilisateur(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    nom = db.Column(db.String(254), nullable=False)
    dateNaissance = db.Column(db.Date, nullable=False)
    email = db.Column(db.String(254), nullable=True)
    numeroTelephone = db.Column(db.String(254), nullable=True)
    province = db.Column(db.String(254), nullable=False)
    commune = db.Column(db.String(254), nullable=False)

    def to_dict(self):
        return {
                "id": self.id,
                "nom": self.nom,
                "dateNaissance": self.dateNaissance,
                "email": self.email,
                "numeroTelephone": self.numeroTelephone,
                "province": self.province,
                "commune": self.commune,
                }
