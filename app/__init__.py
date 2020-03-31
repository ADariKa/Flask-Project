from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from flask_mail import Mail, Message

from config import Develop, Testing

app = Flask(__name__)
app.config.from_object(Develop)

db = SQLAlchemy(app)

from app import models

migrate = Migrate(app, db)
login_manager = LoginManager(app)
mail = Mail(app)


def get_session() -> db.Session:
    return db.session
