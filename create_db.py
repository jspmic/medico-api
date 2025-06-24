from api import app
from src.models.models import db

with app.app_context():
    db.create_all()
