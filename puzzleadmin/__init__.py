import os
import os.path as op
from flask import Flask, url_for, redirect, jsonify, Blueprint, render_template
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin, LoginManager,current_user, login_user
from flask_admin import Admin, form,  expose, AdminIndexView, BaseView, expose
from flask_admin.contrib.sqla import ModelView
from flask_admin.contrib import sqla
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, ValidationError
from wtforms.validators import InputRequired, Length
from sqlalchemy.ext.declarative import DeclarativeMeta
from datetime import datetime
from jinja2 import Markup
from flask_bootstrap import Bootstrap
import json

app = Flask(__name__, instance_relative_config=True)
app.config.from_object("config.BaseConfig")

bootstrap = Bootstrap(app)

db = SQLAlchemy(app)
db.Model.metadata.reflect(db.engine)

login_manager = LoginManager(app)

@login_manager.user_loader
def load_user(id):
    return Admins.query.get(id)

class User(db.Model, UserMixin):
    __table__ = db.Model.metadata.tables['users']

class Tag(db.Model):
    __table__ = db.Model.metadata.tables['tags']

class Product(db.Model):
    __table__ = db.Model.metadata.tables['products']
    tags = db.relationship('Tag', secondary="productstags",
                            backref=db.backref('products', lazy='dynamic'))

class ProductsTags(db.Model):
    __table__ = db.Model.metadata.tables['productstags']

class CartItem(db.Model):
    __table__ = db.Model.metadata.tables['cartitems']

class Cart(db.Model):
    __table__ = db.Model.metadata.tables['carts']

class Order(db.Model):
    __table__ = db.Model.metadata.tables['orders']

class Address(db.Model):
    __table__ = db.Model.metadata.tables['addresses']

class Rating(db.Model):
    __table__ = db.Model.metadata.tables['ratings']

class Role(db.Model):
    __table__ = db.Model.metadata.tables['roles']

class AdminsRoles(db.Model):
    __table__ = db.Model.metadata.tables['adminsroles']

class Admins(db.Model, UserMixin):
    __table__ = db.Model.metadata.tables['admins']
    roles = db.relationship('Role', secondary="adminsroles",
                            backref=db.backref('admins', lazy='dynamic'))

file_path = op.join(op.dirname(__file__), 'static/img')

class AuthView(sqla.ModelView):
    can_delete = False
    can_export = True

    def is_accessible(self):
        return current_user.is_authenticated

    def inaccessible_callback(self, name):
        return redirect(url_for('login'))

class ProductView(AuthView):
    def is_accessible(self):
        roles = [r.name for r in current_user.roles]
        return 'product_manager' in roles or 'master' in roles

    def inaccessible_callback(self, name):
        return redirect(url_for('login'))

    def _list_thumbnail(self, view, model, name):
        print(model.imagepath)
        if not model.imagepath:
            return ''

        return Markup('<img src="%s">' % url_for('static', filename=form.thumbgen_filename('img/'+model.imagepath)))

    column_formatters = {
        'imagepath': _list_thumbnail
    }

    form_overrides = {
        'imagepath': form.ImageUploadField
    }

    form_args = {
        'imagepath': {
            'label': 'Image',
            'base_path': file_path,
            'allow_overwrite': False,
            'thumbnail_size': (100, 100, True)
        }
    }
    
    column_hide_backrefs = False
    column_list = ('id', 'name', 'price', 'description', 'imagepath', 'rating', 'difficulty', 'quantity', 'tags')
    column_searchable_list = ['id', 'name', 'price', 'description', 'imagepath', 'rating', 'difficulty', 'quantity']

class HomeView(AdminIndexView):
    def is_accessible(self):
        return current_user.is_authenticated  

    def inaccessible_callback(self, name):
        return redirect(url_for('login'))

class AlchemyEncoder(json.JSONEncoder):

    def default(self, obj):
        if isinstance(obj.__class__, DeclarativeMeta):
            # an SQLAlchemy class
            fields = {}
            for field in [x for x in dir(obj) if not x.startswith('_') and x != 'metadata']:
                data = obj.__getattribute__(field)
                try:
                    json.dumps(data) # this will fail on non-encodable values, like other classes
                    fields[field] = data
                except TypeError:
                    fields[field] = None
            # a json-encodable dict
            return fields

        return json.JSONEncoder.default(self, obj)

class AnalyticsView(BaseView):
    def is_accessible(self):
        roles = [r.name for r in current_user.roles]
        return 'sales_manager' in roles or 'master' in roles

    def inaccessible_callback(self, name):
        return redirect(url_for('login'))

    @expose('/')
    def index(self):
        try:
            orders = Order.query.all()
            assert len(orders) >= 0
            users = User.query.all()
            active_users = [user for user in users if user.is_active]
            little_products = [product for product in Product.query.all() if product.quantity < 5]

            return self.render('analytics_index.html', orders=orders, active_users=len(active_users), little_products=little_products)
        except AssertionError as e:
            print(e)
            return redirect('/admin')


app.config['FLASK_ADMIN_SWATCH'] = 'cerulean'
admin = Admin(app, name='PuzzlShop', template_mode='bootstrap3', index_view=HomeView(name='Home'))
admin.add_view(AuthView(User, db.session))
admin.add_view(ProductView(Product, db.session))
admin.add_view(AuthView(Address, db.session))
admin.add_view(AnalyticsView(name='Analytics', endpoint='analytics'))
admin.add_view(AuthView(Tag, db.session))
admin.add_view(AuthView(Order, db.session))

class LoginForm(FlaskForm):
    username = StringField('Username', validators=[InputRequired(), Length(min=4, max=60)])
    password = PasswordField('Password', validators=[InputRequired(), Length(min=4, max=80)])

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect('/admin')
    else:
        form = LoginForm()
        if form.validate_on_submit():
            admin = Admins.query.filter_by(name=form.username.data).first()
            if admin:
                if admin.password == form.password.data:
                    login_user(admin)
                    return redirect('/admin')
            return '<h1>Invalid username or password</h1>'

        return render_template('login.html', form=form)
app.run()