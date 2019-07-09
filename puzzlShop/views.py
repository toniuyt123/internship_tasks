from flask import Flask, render_template, redirect, url_for, request, flash, Blueprint
from werkzeug.security import generate_password_hash, check_password_hash
import phonenumbers
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from wtforms.validators import InputRequired, Email, Length, EqualTo
from puzzlShop.email_token import generate_confirmation_token, confirm_token, send_email
from puzzlShop import app, AlchemyEncoder, bootstrap, db, Tag, login_manager, Rating, User, Product, Cart, CartItem, stripe_keys, Order, Address
from operator import itemgetter
import json
import ast
import csv
import os
from datetime import datetime
import stripe
from .forms import LoginForm, RegisterForm, AddressForm, EmailForm, PasswordForm


@app.route('/')
@app.route('/index')
def index():
    deals = db.engine.execute(""" SELECT p.*, d.newprice FROM Products p
                                    INNER JOIN Deals d ON d.productid = p.id
                                    WHERE d.startdate <= NOW() AND d.enddate >= NOW()
                                    LIMIT 5;""")
    return render_template('index.html', deals=deals)


@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()
    try:
        if request.method == 'POST' and form.validate():
            hashed_password = generate_password_hash(
                form.password.data, method='sha256')
            user = User(username=form.username.data, phone=form.phone.data, country=form.country.data,
                        email=form.email.data, passwordhash=hashed_password)
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
    keys = []
    page = 1
    min_price, max_price = 0, 1000
    selected_tags = []
    if request.method == 'POST':
        try:
            keys = list(request.form.keys())
            statement = ''
            result = []
            if 'search_query' in keys:
                query = request.form['search_query']
                result = db.engine.execute('''SELECT * FROM products 
                                WHERE to_tsvector(name) @@ to_tsquery(%s) OR
                                    to_tsvector(description) @@ to_tsquery(%s)''', (query, query))
            tags = [t.name for t in Tag.query.all()]
            if 'tags' in keys:
                tags = request.form.getlist('tags')
                selected_tags = request.form.getlist('tags')
            req_min, req_max = request.form.get('min'), request.form.get('max')
            if req_min != None and req_min != '':
                print(request.form.get('min'))
                min_price = int(req_min)
            if req_max != None and req_max != '':
                max_price = int(req_max)
            statement = ('''SELECT p.*, array_agg(t.name) AS tags FROM products p
                            LEFT JOIN productstags pt ON pt.productid = p.id
                            LEFT JOIN tags t ON pt.tagid = t.id
                            WHERE p.price >= %s AND p.price <= %s
                            GROUP BY p.id, p.name, p.description, p.price, p.difficulty, p.rating, p.quantity
                            HAVING \'%s\' = ANY(array_agg(t.name))''' % (min_price, max_price, tags[0])) + ''.join((' OR \'%s\' = ANY(array_agg(t.name))' % t for t in tags[1:]))
            print(statement)
            result = db.engine.execute(statement)
            products = [dict(row.items()) for row in result]
            if 'page' in keys:
                page = request.form.get('page')
            assert int(page) <= len(products) / 20
        except AssertionError:
            return redirect('/')
    if products == []:
        products = Product.query.all()

    if 'sort_by' in keys:
        params = json.loads(request.form.get('sort_by').replace("'", "\""))
        desc = True if params['desc'] == 'True' else False
        #products.sort(key=lambda x: getattr(x, params['param']), reverse=desc)
        products = sorted(products, key=itemgetter(
            params['param']), reverse=desc)

    tags = db.engine.execute('SELECT * FROM tags')
    
    deals = db.engine.execute('SELECT * FROM deals WHERE startdate <= NOW() AND enddate >= NOW()')

    return render_template('/products.html', products=products, tags=tags, page=int(page), 
                        deals=deals, selected_tags=selected_tags, prices_range=(min_price, max_price))


@app.route('/products/<id>', methods=['GET'])
def product_details(id):
    product = Product.query.filter_by(id=id).first_or_404()
    review_count = db.engine.execute(""" SELECT COUNT(*) FROM Ratings WHERE productid = %s
    """, (product.id,)).fetchone()[0]
    print(review_count)
    return render_template('product_details.html', product=product, review_count=review_count)


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
        quantity = 1 if 'quantity' not in request.form.keys() else int(
            request.form['quantity'])
        cart.remove_from_cart(product, quantity)

    return redirect(url_for('cart'))


@app.route('/cart', methods=['GET', 'POST'])
def cart():
    form = AddressForm()

    if not current_user.is_authenticated:
        return redirect(url_for('login'))
    else:
        cart = get_cart(current_user.id)
        cartitems = db.session.query(CartItem, Product).filter(
            CartItem.cartid == cart.id).filter(CartItem.productid == Product.id).all()

        return render_template('cart.html', cartitems=cartitems, form=form, key=stripe_keys['publishable_key'],
                               empty=True if cartitems == [] else False)


def get_cart(id):
    cart = Cart.query.filter_by(
        userid=current_user.id, cartmode='active').first()
    if not cart:
        cart = Cart(userid=current_user.id, createdat=datetime.now())
        db.session.add(cart)
        db.session.commit()
    return cart


@app.route('/charge', methods=['POST', 'GET'])
def charge():
    form = AddressForm()
    if form.validate_on_submit():
        try:
            address = Address(address=form.street.data, city=form.city.data,
                            state=form.state.data, country=form.country.data, zip=form.zipCode.data)
            db.session.add(address)

            # Amount in cent
            amount = int(float(request.form['amount']) * 100)
            assert amount > 0

            cartid = request.form['cart']

            cart = Cart.query.filter_by(id=cartid).first()

            result = db.engine.execute(""" SELECT SUM(p.price) FROM cartitems c
                                                LEFT JOIN products p ON p.id = c.productid
                                                WHERE c.cartid = %s
                                                GROUP BY c.cartid""", (cartid,))
            real_amount = -1
            for row in result:
                real_amount = int(row[0]*100)
            if amount != real_amount:
                return redirect(url_for('cart'))

            cart.cartmode = 'quote'
            db.session.add(cart)
            user = User.query.filter_by(id=cart.userid).first_or_404()

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

            order = Order(userid=user.id, cartid=cartid, orderedat=datetime.now(
            ), addressid=address.id, orderammount=amount / 100)
            db.session.add(order)
            db.session.commit()
            return render_template('charge.html', amount=amount)
        except (stripe.error.StripeError, AssertionError) as e:
            print(e)
            db.session.rollback()
    return redirect(url_for('cart'))


@app.route('/cartitem_delete', methods=['GET', 'POST'])
def delete_item():
    cartid = request.args['cartid']
    productid = request.args['productid']
    item = CartItem.query.filter_by(cartid=cartid, productid=productid).first()
    db.session.delete(item)
    db.session.commit()

    return redirect(url_for('cart'))


@app.route('/reset', methods=["GET", "POST"])
def reset():
    form = EmailForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first_or_404()

        subject = "Password reset requested"
        token = generate_confirmation_token(form.email.data)
        recover_url = url_for(
            'reset_with_token',
            token=token,
            _external=True)

        html = render_template(
            'recover.html',
            recover_url=recover_url)

        send_email(user.email, subject, html)

        return redirect(url_for('index'))
    return render_template('reset.html', form=form)


@app.route('/reset/<token>', methods=["GET", "POST"])
def reset_with_token(token):
    try:
        email = confirm_token(token)
    except:
        flash('The confirmation link is invalid or has expired.', 'danger')

    form = PasswordForm()

    if form.validate_on_submit():
        user = User.query.filter_by(email=email).first_or_404()

        hashed_password = generate_password_hash(
            form.password.data, method='sha256')
        user.passwordhash = hashed_password

        db.session.add(user)
        db.session.commit()

        return redirect(url_for('login'))

    return render_template('reset_with_token.html', form=form, token=token)


@app.route('/rate', methods=['POST'])
def rate():
    if current_user.is_authenticated:
        product = Product.query.filter_by(
            id=request.form.get('productid')).first_or_404()
        rate = request.form.get('rate')

        rating = Rating.query.filter_by(
            userid=current_user.id, productid=product.id).first()
        if not rating:
            rating = Rating(userid=current_user.id,
                            productid=product.id, rating=rate)
        else:
            rating.rating = rate
        db.session.add(rating)
        db.session.commit()

        return redirect("/products/%s" % (product.id,))
    else:
        return redirect(url_for('login'))