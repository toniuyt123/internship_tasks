from flask import Flask, render_template, redirect, url_for, request
from flask_wtf import FlaskForm
from flask_bootstrap import Bootstrap
from flask_sqlalchemy import SQLAlchemy
from wtforms import StringField, PasswordField, BooleanField, ValidationError
from wtforms.validators import InputRequired, Email, Length, EqualTo
from werkzeug.security import generate_password_hash, check_password_hash
import phonenumbers
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from wtforms.validators import InputRequired, Email, Length, EqualTo

app = Flask(__name__)
app.config.from_object('config.BaseConfig')
bootstrap = Bootstrap(app)

db = SQLAlchemy(app)
db.Model.metadata.reflect(db.engine)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

class User(db.Model, UserMixin):
    __table__ = db.Model.metadata.tables['users']

    def __repr__(self):
        return self.DISTRICT

@login_manager.user_loader
def get_user(id):
  return User.query.get(int(id))

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

@app.route('/')
@app.route('/index')
def index():
    return render_template('index.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()
    try:
        if request.method == 'POST' and form.validate():
            hashed_password = generate_password_hash(form.password.data, method='sha256')
            new_user = User(username=form.username.data, email=form.email.data, phone=form.phone.data, passwordhash=hashed_password)
            db.session.add(new_user)
            db.session.commit()
            return redirect(url_for('login'))
        return render_template('register.html', form=form)
    except Exception as e:
        print("Error is:" + str(e))
        return render_template('register.html', form=form)


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user:
            if check_password_hash(user.passwordhash, form.password.data):
                login_user(user, remember=form.remember.data)
                return redirect('/')

        return '<h1>Invalid username or password</h1>'

    return render_template('login.html', form=form)

if __name__=='__main__':
    app.run()