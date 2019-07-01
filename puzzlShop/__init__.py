import os
import os.path as op
from flask import Flask, url_for, redirect
from flask_mail import Mail
from flask_bootstrap import Bootstrap
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, current_user
from flask_admin import Admin, form,  expose, AdminIndexView
from flask_admin.contrib.sqla import ModelView
from flask_admin.contrib import sqla
from jinja2 import Markup
from datetime import datetime
import stripe
import csv

app = Flask(__name__, instance_relative_config=True)
app.config.from_object("puzzlShop.config.BaseConfig")
mail = Mail(app)
bootstrap = Bootstrap(app)

db = SQLAlchemy(app)
db.Model.metadata.reflect(db.engine)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'


stripe_keys = {
  'secret_key': os.environ['SECRET_KEY'],
  'publishable_key': os.environ['PUBLISHABLE_KEY']
}

stripe.api_key = stripe_keys['secret_key']

@login_manager.user_loader
def get_user(id):
  return User.query.get(int(id))

class User(db.Model, UserMixin):
    __table__ = db.Model.metadata.tables['users']

class Product(db.Model):
    __table__ = db.Model.metadata.tables['products']

class CartItem(db.Model):
    __table__ = db.Model.metadata.tables['cartitems']

class Cart(db.Model):
    __table__ = db.Model.metadata.tables['carts']

    def add_to_cart(self, productId, quantity):
        cartitems = db.session.query(Cart, CartItem).filter(CartItem.cartid == self.id).all()
        current_items = [item[1].productid for item in cartitems]
        if productId in current_items:
            item = db.session.query(CartItem).filter(CartItem.cartid == self.id).filter(CartItem.productid == productId).first()
            item.quantity += quantity
            db.session.add(item)
        else:
            newItem = CartItem(cartid=self.id, productid=productId, quantity=quantity, createdat=datetime.now())
            db.session.add(newItem)
        db.session.commit()

    def remove_from_cart(self, productId, quantity):
        cartitems = db.session.query(Cart, CartItem).filter(CartItem.cartid == self.id).all()
        current_items = [item[1].productid for item in cartitems]
        if productId in current_items:
            item = db.session.query(CartItem).filter(CartItem.cartid == self.id).filter(CartItem.productid == productId).first()
            item.quantity -= quantity
            if item.quantity == 0:
                db.session.delete(item)
            else:
                db.session.add(item)
            db.session.commit()

class Order(db.Model):
    __table__ = db.Model.metadata.tables['orders']

class Address(db.Model):
    __table__ = db.Model.metadata.tables['addresses']

file_path = op.join(op.dirname(__file__), 'static/img')

class AuthView(sqla.ModelView):
    can_delete = False
    can_export = True

    def is_accessible(self):
        if current_user.is_authenticated:
            return current_user.is_admin
        return False

    def inaccessible_callback(self, name):
        return redirect(url_for('login'))

class ProductView(AuthView):
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

class HomeView(AdminIndexView):
    def is_accessible(self):
        if current_user.is_authenticated:
            return current_user.is_admin
        return False

    def inaccessible_callback(self, name):
        return redirect(url_for('login'))

app.config['FLASK_ADMIN_SWATCH'] = 'cerulean'
admin = Admin(app, name='PuzzlShop', template_mode='bootstrap3', index_view=HomeView(name='Home'))
admin.add_view(AuthView(User, db.session))
admin.add_view(ProductView(Product, db.session))
admin.add_view(AuthView(Address, db.session))

import puzzlShop.views