from flask_wtf import Form
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired # basic data validator
from wtforms.validators import Email, Length

class SignupForm(Form):
    first_name = StringField('First name', validators=[DataRequired("Please enter your first name."), Length(min=2, max=100, message="Invalid first name.")])
    last_name = StringField('Last name', validators=[DataRequired("Please enter your last name."), Length(min=2, max=100, message="Invalid last name.")])
    email = StringField('Email', validators=[DataRequired("Please enter your email."), Email("Please enter a valid email address."), Length(min=6, max=120, message="Invalid email.")])
    password = PasswordField('Password', validators=[DataRequired("Please enter your password."), Length(min=8, message="Your password should be 8 characters or more.")])
    submit = SubmitField('Sign up')
