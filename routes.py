# Will contain the applications main code.

import os
import ujson as json
import requests

from collections import namedtuple
from flask import Flask, render_template, request, session, redirect, url_for, abort
from flask_login import current_user, LoginManager, login_required, login_user, logout_user

from models import db, User, Place
from forms import SignupForm, LoginForm, AddressForm

app = Flask(__name__)

# we do not use the SQLAlchemy event system
# turning it off saves some resources
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Database configuration
DATABASE_URL = 'postgresql://localhost/locationbasedservice'
if 'DATABASE_URL' in os.environ:
    DATABASE_URL = os.environ['DATABASE_URL']

app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE_URL
# app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///data.db'
db.init_app(app)

# Prevent CSRF attack (form)
app.secret_key = 'development-key'

# login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# Named tuples
Geolocation = namedtuple('Geolocation',
                         'city country_code country_name ip latitude longitude metro_code region_code region_name time_zone zip_code')


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/about')
def about():
    return render_template('about.html')


@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if current_user.is_authenticated:
        return redirect(url_for('home'))

    form = SignupForm()

    if request.method == 'GET':
        return render_template('signup.html', form=form)

    elif request.method == 'POST':
        if form.validate() == False:
            return render_template('signup.html', form=form)
        else:
            user = User(form.first_name.data, form.last_name.data, form.email.data, form.password.data)
            db.session.add(user)
            db.session.commit()

            login_user(user)
            return redirect(url_for('home'))


@app.route('/home', methods=['GET', 'POST'])
@login_required
def home():
    form = AddressForm()
    p = Place()

    if request.method == 'GET':
        places = []
        gl = session.get('_location', None)
        gl = get_user_location() if gl is None else Geolocation(*gl)
        if gl is None:
            form.address.data = 'London, UK'
        else:
            form.address.data = '{}, {}, {} {}'.format(gl.city, gl.region_name, gl.country_name, gl.zip_code)

        my_coordinates = p.address_to_latlng(form.address.data)
        if not all(my_coordinates):
            # failed to decode address to lat, lng
            form.address.errors += ('Invalid address', ) # form.address.errors is a immutable tuple
        else:
            places = p.query(form.address.data)

        return render_template('home.html', form=form, my_coordinates=my_coordinates, places=places)

    elif request.method == 'POST':
        if form.validate() == False:
            return render_template('home.html', form=form)
        else:
            # get the address
            address = form.address.data

            # query for places around the address
            my_coordinates = p.address_to_latlng(address)
            places = p.query(address)

            # return the results as a list
            return render_template('home.html', form=form, my_coordinates=my_coordinates, places=places)


@app.route('/login', methods=['GET', 'POST'])
def login():
    # Fetch location regardless of user login state
    session['_location'] = get_user_location()

    if current_user.is_authenticated:
        return redirect(url_for('home'))

    form = LoginForm()

    if request.method == 'GET':
        return render_template('login.html', form=form)

    elif request.method == 'POST':
        if form.validate() == False:
            return render_template('login.html', form=form)
        else:
            email = form.email.data
            password = form.password.data

            user = User.query.filter_by(email=email).first()
            if user is not None and user.check_password(password):
                login_user(user)
                return redirect(url_for('home'))
            else:
                form.email.errors.append('Invalid email or password')
                return render_template('login.html',
                                       form=form)  # redirect to login url - which triggers a GET request from the browser


@app.route('/logout')
@login_required
def logout():
    logout_user()
    session.pop('_location', None)
    return redirect(url_for('index'))


# callback to reload the user object
@login_manager.user_loader
def load_user(id):
    return User.query.get(int(id))


# helper methods

# get the location based on his IP
def get_user_location():
    """ Finds the location of the user based on his IP, constructs and returns a Geolocation namedtuple"""
    url = 'http://freegeoip.net/json'
    ip = request.environ.get('HTTP_X_REAL_IP', request.remote_addr)
    if ip != '127.0.0.1':
        url += '/q=%s' % ip

    r = requests.get(url)
    if r.status_code is not 200:
        return None

    j = json.loads(r.text)
    gl = Geolocation(
        city=j['city'],
        country_code=j['country_code'],
        country_name=j['country_name'],
        ip=j['ip'],
        latitude=j['latitude'],
        longitude=j['longitude'],
        metro_code=j['metro_code'],
        region_code=j['region_code'],
        region_name=j['region_name'],
        time_zone=j['time_zone'],
        zip_code=j['zip_code'],
    )
    return gl


# initialize the database
def init_db():
    with app.app_context():
        # SQLAlchemy now knows what the 'current' app is while within this block
        # therefore, you can now run:
        db.create_all()
        print('Database created.')


if __name__ == '__main__':
    if 'MODE' in os.environ and os.environ['MODE'].strip() == 'production':
        app.run()
    else:
        app.run(debug=True)  # development mode
