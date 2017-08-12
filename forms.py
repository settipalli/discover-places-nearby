from flask_wtf import Form
from wtforms import StringField, PasswordFiled, SubmitField

class SignupForm(Form):
    first_name = StringField('First name')
    last_name = StringField('Last name')
    email = StringField('Email')
    password = PasswordFiled('Password')
    submit = SubmitField('Sign up')
