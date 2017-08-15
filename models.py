from flask_sqlalchemy import SQLAlchemy
from werkzeug import generate_password_hash, check_password_hash
from datetime import datetime

import geocoder
import urllib
import json

db = SQLAlchemy()


class User(db.Model):
    __tablename__ = 'users'
    uid = db.Column(db.Integer, primary_key=True)
    firstname = db.Column(db.String(100))
    lastname = db.Column(db.String(100))
    email = db.Column(db.String(120), unique=True)
    pwdhash = db.Column(db.String(254))

    def __init__(self, firstname, lastname, email, password):
        self.firstname = firstname.title()
        self.lastname = lastname.title()
        self.email = email.lower()
        self.set_password(password)

    def set_password(self, password):
        self.pwdhash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.pwdhash, password)

    # login friendly methods - https://blog.miguelgrinberg.com/post/the-flask-mega-tutorial-part-v-user-logins
    @property
    def is_authenticated(self):
        # should just return True unless the object represents a user that should not be allowed to authenticate for
        # some reason.
        return True

    @property
    def is_active(self):
        #  should return True for users unless they are inactive, for example because they have been banned
        return True

    @property
    def is_anonymous(self):
        # should return True only for fake users that are not supposed to log in to the system
        return False

    def get_id(self):
        # return a unique identifier for the user, in unicode format
        # use the unique id generated by the database layer for this
        return str(self.uid)

    def __repr__(self):
        return '<User %r %r>' % (self.firstname, self.lastname)


# p = Place()
# places = p.query("London Eye, Lambeth, London")
# lat: 51.503324  lng: -0.119543
class Place(object):
    def meters_to_walking_time(self, meters):
        # 80 meters is 1 minute walking time
        return int(meters / 80)

    def wiki_path(self, slug):
        return urllib.parse.urljoin('http://en.wikipedia.org/wiki/', slug.replace(' ', '_'))

    def address_to_latlng(self, address):
        # check if the address exists in the 'locations' table
        location = Location.query.filter(Location.address.like(address.lower() + "%")).first()
        if location is not None:
            # add repeated record
            repeated_location = Repeated(location)
            db.session.add(repeated_location)
            db.session.commit()
            return (location.lat, location.lng)
        else:
            g = geocoder.google(address)
            self.save_location(g)
            return (g.lat, g.lng)

    def query(self, address):
        lat, lng = self.address_to_latlng(address)

        query_url = 'https://en.wikipedia.org/w/api.php?action=query&list=geosearch&gsradius=5000&gscoord={0}%7C{1}&gslimit=20&format=json'.format(lat, lng)
        g = urllib.request.urlopen(query_url)
        results = g.read()
        g.close()

        data = json.loads(results)

        places = []
        for place in data['query']['geosearch']:
            name = place['title']
            meters = place['dist']
            lat = place['lat']
            lng = place['lon']

            wiki_url = self.wiki_path(name)
            walking_time = self.meters_to_walking_time(meters)

            d = {
                'name': name,
                'url': wiki_url,
                'time': walking_time,
                'lat': lat,
                'lng': lng
            }

            places.append(d)

        return places


    def save_location(self, geocoder):
        # add location
        g = geocoder
        lat = g.lat
        lng = g.lng
        address = g.location
        computedaddress = g.address.strip()
        city = g.city
        state = g.state
        country = g.raw['country']['long_name']
        countrycode = g.country
        postalcode = g.postal
        confidence = g.confidence
        url = g.url.rsplit('&key')[0]

        location = Location(lat, lng, address, computedaddress, city, state, country, countrycode, postalcode,
                            confidence, url)
        db.session.add(location)
        db.session.commit()


# location cache
class Location(db.Model):
    __tablename__ = 'locations'
    lid = db.Column(db.Integer, primary_key=True)
    lat = db.Column(db.Float)
    lng = db.Column(db.Float)
    address = db.Column(db.String(254))
    computedaddress = db.Column(db.String(254))
    city = db.Column(db.String(100))
    state = db.Column(db.String(100))
    country = db.Column(db.String(100))
    countrycode = db.Column(db.String(5))
    postalcode = db.Column(db.String(20))
    confidence = db.Column(db.Integer)
    url = db.Column(db.String(254))
    
    def __init__(self, lat, lng, address, computedaddress, city, state, country, countrycode, postalcode, confidence, url):
        self.lat = lat
        self.lng = lng
        self.address = address.lower() if address is not None else ""
        self.computedaddress = computedaddress if computedaddress is not None else ""
        self.city = city.title() if city is not None else ""
        self.state = state.upper() if state is not None else ""
        self.country = country.title() if country is not None else ""
        self.countrycode = countrycode.upper() if countrycode is not None else ""
        self.postalcode = postalcode if postalcode is not None else ""
        self.confidence = confidence
        self.url = url


# counter - repeated address queries
class Repeated(db.Model):
    __tablename__ = 'repeated'
    cid = db.Column(db.Integer, primary_key=True)
    timestamp = db.Column(db.DateTime)
    location_id = db.Column(db.Integer, db.ForeignKey('locations.lid'))
    location = db.relationship('Location', backref=db.backref('locations', lazy='dynamic'))

    def __init__(self, location, timestamp = None):
        if timestamp is None:
            timestamp = datetime.utcnow()
        self.timestamp = timestamp
        self.location = location

