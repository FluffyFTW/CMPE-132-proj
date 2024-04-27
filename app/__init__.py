import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
myapp_obj = Flask(__name__)

basedir = os.path.abspath(os.path.dirname(__file__))

myapp_obj.config.from_mapping(
    SECRET_KEY = 'you-will-never-guess',
    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir, 'app.db'),
    SQLALCHEMY_TRACK_MODIFICATIONS = False
)

db = SQLAlchemy(myapp_obj)
login = LoginManager(myapp_obj)

try:
    from app.features.models import user
except ImportError:
    pass

# with myapp_obj.app_context():
#     existing_user = user.query.filter_by(username = db.String("super_admin")).first()

#     if existing_user == None:
#         new_user = user(username = db.String("super_admin"), perms = db.String("Admin"))
#         new_user.set_password(db.String("super_password123"))
#         db.session.add(new_user)
#         db.session.commit()

    login.login_view = 'login'

from app import routes