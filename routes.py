# Will contain the applications main code.

from flask import Flask, render_template, request, session, redirect, url_for, abort
from flask_login import current_user, LoginManager, login_required, login_user, logout_user

from models import db, User, Place
from forms import SignupForm, LoginForm, AddressForm

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://localhost/locationbasedservice'
db.init_app(app)

# Prevent CSRF attack (form)
app.secret_key = "development-key"

# login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/about")
def about():
    return render_template("about.html")


@app.route("/signup", methods=["GET", "POST"])
def signup():
    if current_user.is_authenticated:
        return redirect(url_for("home"))

    form = SignupForm()

    if request.method == "GET":
        return render_template("signup.html", form=form)

    elif request.method == "POST":
        if form.validate() == False:
            return render_template("signup.html", form=form)
        else:
            user = User(form.first_name.data, form.last_name.data, form.email.data, form.password.data)
            db.session.add(user)
            db.session.commit()

            login_user(user)
            return redirect(url_for("home"))


@app.route("/home", methods=["GET", "POST"])
@login_required
def home():
    form = AddressForm()
    places = []
    my_coordinates = (37.4221, -122.0844)

    if request.method == "GET":
        return render_template("home.html", form=form, my_coordinates=my_coordinates, places=places)

    elif request.method == "POST":
        if form.validate() == False:
            return render_template("home.html", form=form)
        else:
            # get the address
            address = form.address.data

            # query for places around the address
            p = Place()
            my_coordinates = p.address_to_latlng(address)
            places = p.query(address)

            # return the results as a list
            return render_template("home.html", form=form, my_coordinates=my_coordinates, places=places)

@app.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("home"))

    form = LoginForm()

    if request.method == "GET":
        return render_template("login.html", form=form)

    elif request.method == "POST":
        if form.validate() == False:
            return render_template("login.html", form=form)
        else:
            email = form.email.data
            password = form.password.data

            user = User.query.filter_by(email=email).first()
            if user is not None and user.check_password(password):
                login_user(user)
                return redirect(url_for("home"))
            else:
                form.email.errors.append("Invalid email or password")
                return render_template("login.html", form=form) # redirect to login url - which triggers a GET request from the browser


@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("index"))


# callback to reload the user object
@login_manager.user_loader
def load_user(id):
    return User.query.get(int(id))


if __name__ == "__main__":
    app.run(debug=True)
