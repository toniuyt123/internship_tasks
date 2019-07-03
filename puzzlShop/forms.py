from flask_wtf import FlaskForm, RecaptchaField
from wtforms import StringField, PasswordField, BooleanField, ValidationError, SelectField
from wtforms.validators import InputRequired, Email, Length, EqualTo
import os
import csv


class LoginForm(FlaskForm):
    username = StringField('Username', validators=[InputRequired(), Length(min=4, max=60)])
    password = PasswordField('Password', validators=[InputRequired(), Length(min=8, max=80)])
    remember = BooleanField('Remember me')

class RegisterForm(FlaskForm):
    email = StringField('Email', validators=[InputRequired(), Email(message='Invalid email'), Length(max=100)])
    username = StringField('Username', validators=[InputRequired(), Length(min=4, max=60)])
    #phone = StringField('phone', validators=[])
    password = PasswordField('Password', validators=[
        InputRequired(), Length(min=8, max=80),
        EqualTo('confirm', message='Passwords must match')])
    confirm = PasswordField('Confirm Password')
    recaptcha = RecaptchaField()

class AddressForm(FlaskForm):
    countries = []
    abs_path = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'countries.csv')
    with open(abs_path) as cn:
        reg_reader = csv.DictReader(cn, delimiter=',')
        for row in reg_reader:
            countries.append( (row['Alpha-3 code'][2:-1], row['Country']) )
    street = StringField('Street', validators=[InputRequired(), Length(max=200)])
    city = StringField('City', validators=[InputRequired(), Length(max=85)])
    state = StringField('State', validators=[InputRequired(), Length(max=85)])
    country = SelectField('Country', choices = countries, validators = [InputRequired()])
    zipCode = StringField('Zip', validators=[InputRequired(), Length(max=10)])

class EmailForm(FlaskForm):
    email = StringField('Email', validators=[InputRequired(), Email(message='Invalid email'), Length(max=100)])

class PasswordForm(FlaskForm):
    password = PasswordField('Password', validators=[
        InputRequired(), Length(min=8, max=80),
        EqualTo('confirm', message='Passwords must match')])
    confirm = PasswordField('Confirm Password')