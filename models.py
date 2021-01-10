from sqlalchemy.sql.schema import ForeignKey
from app import db
from datetime import datetime

# Modelo de usuario
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(15), nullable=False)
    age = db.Column(db.Integer, nullable=False)
    email = db.Column(db.String(45), nullable=False, unique=True)
    username = db.Column(db.String(30), nullable=False, unique=True)
    password = db.Column(db.String(256), nullable=False)
    created_at = db.Column(db.String(50), nullable=False)


# Modelo de post 
class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, foreign_key=True, nullable=False)
    title = db.Column(db.String(30), nullable=False, unique=True)
    topic = db.Column(db.String(25), nullable=False)
    content = db.Column(db.String(550), nullable=False, unique=True)
    public = db.Column(db.Boolean, nullable=False)
    created_at = db.Column(db.String(50), nullable=False)

# BASE PARA LA CLASE DE MODELOS DE POST
#id
#foreign key -> Conectar con el usuario
#title -> Campo unico
#topic  
#content -> Campo unico
#public = True or False  
#created_at  