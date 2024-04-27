from flask_sqlalchemy import SQLAlchemy
from app import login,db
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy.sql import func

class user(db.Model, UserMixin):
    id = db.Column(db.Integer,primary_key = True)
    username = db.Column(db.String(100),nullable=False,unique = True)
    password = db.Column(db.String(100),nullable = False)
    perms = db.Column(db.String(100),nullable = False)
    def check_password(self, password):
        return check_password_hash(self.password, password)
    def set_password(self, password):
        self.password = generate_password_hash(password)

class books(db.Model, UserMixin):
    id = db.Column(db.Integer,primary_key = True)
    title = db.Column(db.String(100),nullable=False,unique = True)
    amount = db.Column(db.Integer(),nullable=False)
    student_only = db.Column(db.Boolean(100), nullable=False)

class book_requests(db.Model, UserMixin):
    id = db.Column(db.Integer,primary_key = True)
    requester_id = db.Column(db.Integer())
    titles = db.Column(db.String(100),nullable=False,unique = True)
    amount = db.Column(db.Integer(),nullable=False)
    student_only = db.Column(db.Boolean(100), nullable=False)
    status = db.Column(db.String(100), nullable=False)

class checkout_list(db.Model, UserMixin):
    id = db.Column(db.Integer,primary_key = True)
    book_id = db.Column(db.Integer(),nullable=False)
    user_id = db.Column(db.Integer(),nullable=False)
    checkout_time = db.Column(db.DateTime(timezone=True), server_default=func.now(), nullable=False)
    checkout_in = db.Column(db.DateTime(timezone=True))
    
@login.user_loader
def load_user(id):
    return user.query.get(int(id))