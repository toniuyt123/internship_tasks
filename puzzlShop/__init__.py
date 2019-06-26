import os
import os.path as op
from flask import Flask, url_for, redirect
from flask_mail import Mail
from flask_bootstrap import Bootstrap
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, current_user
from flask_admin import Admin, form
from flask_admin.contrib.sqla import ModelView
from flask_admin.contrib import sqla
from jinja2 import Markup

app = Flask(__name__, instance_relative_config=True)
app.config.from_object("puzzlShop.config.BaseConfig")
mail = Mail(app)
bootstrap = Bootstrap(app)

db = SQLAlchemy(app)
db.Model.metadata.reflect(db.engine)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'


@login_manager.user_loader
def get_user(id):
  return User.query.get(int(id))

class User(db.Model, UserMixin):
    __table__ = db.Model.metadata.tables['users']

class Product(db.Model):
    __table__ = db.Model.metadata.tables['products']

file_path = op.join(op.dirname(__file__), 'static/img')
class ImageView(sqla.ModelView):
    def is_accessible(self):
        return current_user.is_admin

    def inaccessible_callback(self):
        return redirect(url_for('/login'))

    form_overrides = {
        'imagepath': form.ImageUploadField
    }

    form_args = {
        'imagepath': {
            'label': 'Image',
            'base_path': file_path,
            'allow_overwrite': False
        }
    }

app.config['FLASK_ADMIN_SWATCH'] = 'cerulean'
admin = Admin(app, name='PuzzlShop', template_mode='bootstrap3')
admin.add_view(ModelView(User, db.session))
admin.add_view(ImageView(Product, db.session))

import puzzlShop.views