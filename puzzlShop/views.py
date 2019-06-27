from flask import Flask, render_template, redirect, url_for, request, flash, Blueprint
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, ValidationError
from wtforms.validators import InputRequired, Email, Length, EqualTo
from werkzeug.security import generate_password_hash, check_password_hash
import phonenumbers
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from wtforms.validators import InputRequired, Email, Length, EqualTo
from puzzlShop.email_token import generate_confirmation_token, confirm_token, send_email
from puzzlShop import app, bootstrap, db, login_manager, User, Product, Cart, CartItem, stripe_keys, Order
from operator import itemgetter
import simplejson as json
import ast
from datetime import datetime
import stripe

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
                            HAVING \'%s\' = ANY(array_agg(t.name))''' % (tags[0])) + ''.join((' OR \'%s\' = ANY(array_agg(t.name))' % t for t in tags[1:]))
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

@app.route('/cart/add', methods=['POST'])
def add_to_cart():
    if not current_user.is_authenticated:
        return redirect('/')
    else:
        product = int(request.form['product'])
        cart = get_cart(current_user.id)
        cart.add_to_cart(product, 1)

    return redirect(url_for('cart'))
        
@app.route('/cart/remove', methods=['POST'])
def remove_from_cart():
    if not current_user.is_authenticated:
        return redirect('/')
    else:
        product = int(request.form['product'])
        cart = get_cart(current_user.id)
        quantity = 1 if request.form['quantity'] is None else int(request.form['quantity'])
        cart.remove_from_cart(product, quantity)

    return redirect(url_for('cart'))

@app.route('/cart', methods=['GET', 'POST'])
def cart():
    if not current_user.is_authenticated:
        return redirect(url_for('login'))
    else:
        cart = get_cart(current_user.id)
        cartitems = db.session.query(CartItem, Product).filter(CartItem.cartid == cart.id).filter(CartItem.productid == Product.id).all()

        return render_template('cart.html', cartitems=cartitems, key=stripe_keys['publishable_key'], 
                                empty= True if cartitems == [] else False )

def get_cart(id):
    cart = Cart.query.filter_by(userid=current_user.id,cartmode='active').first()
    if not cart:
        cart = Cart(userid=current_user.id, createdat=datetime.now())
        db.session.add(cart)
        db.session.commit()
    return cart

@app.route('/charge', methods=['POST'])
def charge():
    # Amount in cents
    amount = int(float(request.form['amount']) * 100)
    cartid = request.form['cart']
    print(request.form)
    user = User.query.filter_by(id=cartid).first_or_404()

    customer = stripe.Customer.create(
        email=user.email,
        source=request.form['stripeToken']
    )

    charge = stripe.Charge.create(
        customer=customer.id,
        amount=amount,
        currency='usd',
        description='Flask Charge'
    )
    cart = Cart.query.filter_by(id=cartid).first()
    cart.cartmode = 'quote'
    db.session.add(cart)

    order = Order(userid=user.id, cartid=cartid, orderedat=datetime.now(), addressid=1, orderammount=amount / 100)
    db.session.add(order)
    db.session.commit()

    return render_template('charge.html', amount=amount)

@app.route('/cartitem_delete', methods=['GET', 'POST'])
def delete_item():
    cartid = request.args['cartid']
    productid = request.args['productid']
    item = CartItem.query.filter_by(cartid=cartid, productid=productid).first()
    db.session.delete(item)
    db.session.commit()

    return redirect(url_for('cart'))

if __name__=='__main__':
    app.run()