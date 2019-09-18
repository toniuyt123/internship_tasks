import os
from flask import Flask, abort, render_template
from flask_mail import Mail
from flask_bootstrap import Bootstrap
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin
from flask_socketio import SocketIO
from sqlalchemy.ext.declarative import DeclarativeMeta
from sqlalchemy.engine import Engine
from sqlalchemy.event import listens_for
from sqlalchemy import event
from datetime import datetime
import stripe
import json
import logging
import time

app = Flask(__name__, instance_relative_config=True)
app.config.from_object("puzzlShop.config.BaseConfig")

mail = Mail(app)
bootstrap = Bootstrap(app)

db = SQLAlchemy(app)
db.Model.metadata.reflect(db.engine)

login_manager = LoginManager()
login_manager.init_app(app)

stripe_keys = {
  'secret_key': os.environ['SECRET_KEY'],
  'publishable_key': os.environ['PUBLISHABLE_KEY']
}

stripe.api_key = stripe_keys['secret_key']

socketio = SocketIO(app)

@login_manager.user_loader
def get_user(id):
    return User.query.get(int(id))

class User(db.Model, UserMixin):
    __table__ = db.Model.metadata.tables['users']

    def get_id(self):
        return self.id

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

class Rating(db.Model):
    __table__ = db.Model.metadata.tables['ratings']
        
class Deals(db.Model):
    __table__ = db.Model.metadata.tables['deals']

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

app.jinja_env.add_extension('jinja2.ext.loopcontrols')


'''@db.event.listens_for(db.engine, "handle_error")
def handle_exception(context):
    abort(500)'''


@app.errorhandler(404)
def not_found_error(error):
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_server_error(error):
    db.session.rollback()
    return render_template('500.html'), 500

logging.basicConfig()
logger = logging.getLogger("myapp.sqltime")
logger.setLevel(logging.DEBUG)

@event.listens_for(Engine, "before_cursor_execute")
def before_cursor_execute(conn, cursor, statement,
                        parameters, context, executemany):
    conn.info.setdefault('query_start_time', []).append(time.time())
    logger.debug("Start Query: %s", statement)

@event.listens_for(Engine, "after_cursor_execute")
def after_cursor_execute(conn, cursor, statement,
                        parameters, context, executemany):
    total = time.time() - conn.info['query_start_time'].pop(-1)
    logger.debug("Query Complete!")
    logger.debug("Total Time: %f", total)

import puzzlShop.views

if __name__ == '__main__':
    socketio.run(app, debug=True, threaded=True)
