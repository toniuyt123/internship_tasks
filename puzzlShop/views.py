from flask import Flask, render_template, redirect, url_for, request, flash, Blueprint
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, ValidationError
from wtforms.validators import InputRequired, Email, Length, EqualTo
from werkzeug.security import generate_password_hash, check_password_hash
import phonenumbers
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from wtforms.validators import InputRequired, Email, Length, EqualTo
from puzzlShop.email_token import generate_confirmation_token, confirm_token, send_email
from puzzlShop import app, bootstrap, db, login_manager, User, Product
from operator import itemgetter
import simplejson as json
import ast

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
            user = User(username=form.username.data, email=form.email.data, passwordhash=hashed_password)
            db.session.add(user)
            db.session.commit()

            token = generate_confirmation_token(form.email.data)
            confirm_url = url_for('confirm_email', token=token, _external=True)
            html = render_template('activate.html', confirm_url=confirm_url)
            subject = "Please confirm your email"
            send_email(user.email, subject, html)

            login_user(user)

            return redirect(url_for('login'))
        return render_template('register.html', form=form)
    except Exception as e:
        print("Error is:" + str(e))
        return render_template('register.html', form=form)

@app.route('/confirm/<token>')
@login_required
def confirm_email(token):
    try:
        email = confirm_token(token)
    except:
        flash('The confirmation link is invalid or has expired.', 'danger')

    user = User.query.filter_by(email=email).first_or_404()
    if user.confirmed:
        flash('Account already confirmed. Please login.', 'success')
    else:
        user.confirmed = True
        db.session.add(user)
        db.session.commit()
        flash('You have confirmed your account. Thanks!', 'success')
    return redirect('/')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect('/')
    else: 
        form = LoginForm()
        if form.validate_on_submit():
            user = User.query.filter_by(username=form.username.data).first()
            if user:
                if check_password_hash(user.passwordhash, form.password.data):
                    login_user(user, remember=form.remember.data)
                    return redirect('/')

            return '<h1>Invalid username or password</h1>'

        return render_template('login.html', form=form)

@app.route('/logout', methods=['GET'])
def logout():
    user = current_user
    user.authenticated = False
    db.session.add(user)
    db.session.commit()
    logout_user()
    return redirect('/')

@app.route('/products', methods=['GET', 'POST'])
def get_products():
    products = []
    keys =[]
    if request.method == 'POST':
        keys = list(request.form.keys())
        statement = ''
        result = []
        print(keys)
        if 'search_query' in keys:
            query = request.form['search_query']
            statement = ('''SELECT * FROM products 
                            WHERE to_tsvector(name) @@ to_tsquery(\'%s\') OR
                                to_tsvector(description) @@ to_tsquery(\'%s\')''' % (query, query))
            result = db.engine.execute(statement)
        if 'tags' in keys:
            tags = request.form.getlist('tags')
            print(tags)
            #for tag in tags:
            statement = ('''SELECT p.*, array_agg(t.name) AS tags FROM products p
                            LEFT JOIN productstags pt ON pt.productid = p.id
                            LEFT JOIN tags t ON pt.tagid = t.id
                            GROUP BY p.id, p.name, p.description, p.price, p.difficulty, p.rating, p.quantity
                            HAVING \'%s\' = ANY(array_agg(t.name)); 
            ''' % (tags[0]))
            result = db.engine.execute(statement)
        products = [dict(row.items()) for row in result]
    if products == []:
        products = Product.query.all()

    if 'sort_by' in keys:
        params = json.loads(request.form.get('sort_by').replace("'", "\""))
        desc = True if params['desc'] == 'True' else False
        products.sort(key=lambda x: getattr(x, params['param']), reverse=desc)
        print(products)
    
    tags = db.engine.execute('SELECT * FROM tags')
    
    return render_template('/products.html', products=products, tags=tags)

if __name__=='__main__':
    app.run()