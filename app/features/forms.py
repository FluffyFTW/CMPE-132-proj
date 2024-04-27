from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, IntegerField, SelectField
from wtforms.validators import DataRequired

class login_form(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Remember Me')
    submit = SubmitField('Sign In')

class sign_up_form(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    email = StringField('Email')
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Sign Up')

class edit_profile_form(FlaskForm):
    new_username = StringField('Username', validators=[DataRequired()])
    new_password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Edit')

class order_form(FlaskForm):
    book = StringField('Book Name', validators=[DataRequired()])
    quantity = IntegerField('1')
    student_only = BooleanField('Student Only')
    submit = SubmitField('Order')
    
class checkout_form(FlaskForm):
    book = StringField('Book Name', validators=[DataRequired()])
    submit = SubmitField('Checkout')

class promotion_form(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    role_select = SelectField('Role', choices=[('Admin', 'Admin'), 
                                            ('Librarian', 'Librarian'), 
                                            ('Student_Lib', 'Student Librarian'),
                                            ("Student", "Student"),
                                            ("Public", "Public")])
    submit = SubmitField('Checkout')