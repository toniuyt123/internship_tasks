from flask_wtf import FlaskForm, RecaptchaField
from wtforms import StringField, PasswordField, BooleanField, ValidationError, SelectField
from wtforms.validators import InputRequired, Email, Length, EqualTo
import os
import csv
import phonenumbers

countries = []
phone_codes = []
abs_path = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'countries.csv')
with open(abs_path) as cn:
    reg_reader = csv.DictReader(cn, delimiter=',')
    for row in reg_reader:
        countries.append( (row['ISO3166_1_Alpha_3'], row['Country_Name']) )
        phone_codes.append(('+'+row['Dial'], '+'+row['Dial']))
#phone_codes = sorted(phone_codes)

class LoginForm(FlaskForm):
    username = StringField('Username', validators=[InputRequired(), Length(min=4, max=60)])
    password = PasswordField('Password', validators=[InputRequired(), Length(min=8, max=80)])
    remember = BooleanField('Remember me')

class RegisterForm(FlaskForm):
    email = StringField('Email', validators=[InputRequired(), Email(message='Invalid email'), Length(max=100)])
    username = StringField('Username', validators=[InputRequired(), Length(min=4, max=60)])
    #phone_code = SelectField('Phone Code', choices = phone_codes, validators = [InputRequired()])
    phone = StringField('Phone', validators=[InputRequired()])
    password = PasswordField('Password', validators=[
        InputRequired(), Length(min=8, max=80),
        EqualTo('confirm', message='Passwords must match')])
    country = SelectField('Country', choices = countries, validators = [InputRequired()])
    confirm = PasswordField('Confirm Password')
    recaptcha = RecaptchaField()

    def validate_phone(form, field):
        if len(field.data) > 16:
            raise ValidationError('Invalid phone number.')

        try:
            input_number = phonenumbers.parse(field.data)
            if not (phonenumbers.is_valid_number(input_number)):
                raise ValidationError('Invalid phone number.')
        except:
            try:
                code = 0
                for country in countries:
                    if country[0] == form.country.data:
                        code = phone_codes[countries.index(country)][0]
                input_number = phonenumbers.parse(code+field.data)
                if not (phonenumbers.is_valid_number(input_number)):
                    raise ValidationError('Invalid phone number.')
            except Exception as e:
                raise ValidationError(e)

class AddressForm(FlaskForm):
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