import os
import os.path as op
from flask import Flask, url_for, redirect, jsonify, Blueprint, render_template, request
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin, LoginManager,current_user, login_user
from flask_admin import Admin, form,  expose, AdminIndexView, BaseView, expose
from flask_admin.contrib.sqla import ModelView
from flask_admin.contrib import sqla
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, ValidationError, SelectField, DateField
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

class ReportForm(FlaskForm):
    name = StringField('static field')

class AnalyticsView(BaseView):
    ignore_columns = ['description', 'imagepath', 'name', 'difficulty']
    interval_columns = ['price', 'rating', 'difficulty', 'quantity']

    def is_accessible(self):
        roles = [r.name for r in current_user.roles]
        return 'sales_manager' in roles or 'master' in roles

    def inaccessible_callback(self, name):
        return redirect(url_for('login'))

    def create_form(self, table):
        columns = table.c
        keys = []
        for c in columns:
            if c.name[-2:] == 'id' or c.name in self.ignore_columns:
                continue
            
            if "TIMESTAMP" in str(c.type):
                key = c.name+'_start'
                keys.append(key)
                setattr(ReportForm, key, DateField(key, format='%d-%m-%Y'))
                key = c.name+'_end'
                keys.append(key)
                setattr(ReportForm, key, DateField(key, format='%d-%m-%Y'))
                key = c.name+'_group'
                choices = [('', 'None'), ('year', 'by years'), ('month', 'by months'), 
                            ('week', 'by weeks'), ('day', 'by days'), ('hour', 'by hour')]
                keys.append(key)
                setattr(ReportForm, key, SelectField(key, choices = choices))
            elif c.name in self.interval_columns:
                key = c.name+'_start'
                keys.append(key)
                setattr(ReportForm, key, StringField(key))
                key = c.name+'_end'
                keys.append(key)
                setattr(ReportForm, key, StringField(key))
            elif str(c.type) == 'status':
                keys.append(c.name)
                setattr(ReportForm, c.name, SelectField(key, choices=[('', 'None'), ('ordered', 'ordered'), ('shipped', 'shipped'), ('delivered', 'delivered')]))
            else:   
                keys.append(c.name)
                setattr(ReportForm, c.name, StringField(c.name))
        form = ReportForm()
        return form, keys

    @expose('/products', methods=['GET', 'POST'])
    def products_analytics(self):
        md = db.MetaData()
        table = db.Table('products', md, autoload=True, autoload_with=db.engine)
        form, keys = self.create_form(table)

        products = []
        if request.method == 'POST':
            values = {}
            for field in form:
                if '_start' in field.name:
                    values[field.name] = field.data if field.data is not '' else 0
                elif '_end' in field.name:
                    values[field.name] = field.data if field.data is not '' else 9999

            result = db.engine.execute("""SELECT  id, price, rating, quantity FROM Products
                                        WHERE price >= %s AND price <= %s AND rating >= %s AND rating <= %s AND
                                        quantity >= %s AND quantity <= %s"""
                                          , (values['price_start'], values['price_end'], values['rating_start'],
                                          values['rating_end'], values['quantity_start'], values['quantity_end']))
        else:
            result = {}

        for row in result:
            products.append(row)

        return self.render('product_analytics.html', orders=products, form=form, keys=keys, columns=result.keys())

    @expose('/orders', methods=['GET', 'POST'])
    def orders_analytics(self):
        try:
            md = db.MetaData()
            table = db.Table('orders', md, autoload=True, autoload_with=db.engine)
            form, keys = self.create_form(table)
            
            orders=[]
            if request.method == 'POST':
                startdate = form.orderedat_start.data if form.orderedat_start.data is not None else '01-01-0001'
                enddate = form.orderedat_end.data if form.orderedat_end.data is not None else datetime.now().strftime("%d-%m-%Y")
                enddate = datetime.combine(enddate, datetime.max.time())
                
                status = form.status.data if form.status.data is not '' else 'ordered,shipped,delivered'

                if form.orderedat_group.data == '':
                    result = db.engine.execute(""" SELECT o.orderedat AS orderedat, o.orderammount AS sum, o.status AS status FROM Orders o
                                    WHERE %s <= o.orderedat AND %s >= o.orderedat AND position(o.status::TEXT in %s) > 0
                                    """, (startdate, enddate, status))
                else:
                    result = db.engine.execute(""" SELECT date_trunc(%s, o.orderedat) AS orderedat, SUM(o.orderammount) AS sum, MAX(o.status) AS status FROM Orders o
                                    WHERE %s <= o.orderedat AND %s >= o.orderedat AND position(o.status::TEXT in %s) > 0
                                    GROUP BY 1 """, (form.orderedat_group.data, startdate, enddate, status))
            else:
                result = db.engine.execute("""SELECT orderedat, orderammount AS sum, status FROM Orders o """)

            for row in result:
                orders.append(row)
            assert len(orders) >= 0
            return self.render('orders_analytics.html', orders=orders, form=form, keys=keys, columns=result.keys())
        except AssertionError as e:
            print(e)
            return redirect('/admin')

    @expose('/', methods=['GET'])
    def index(self):
        return self.render('analytics_index.html')


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