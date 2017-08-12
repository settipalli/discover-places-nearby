# Will contain the applications main code.

from flask import Flask, render_template, request, session, redirect, url_for
from models import db, User
from forms import SignupForm

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://localhost/locationbasedservice'
db.init_app(app)

# Prevent CSRF attack (form)
app.secret_key = "development-key"


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/about")
def about():
    return render_template("about.html")


@app.route("/signup", methods=["GET", "POST"])
def signup():
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

            session["email"] = user.email
            return redirect(url_for("home"))


@app.route("/home")
def home():
    return render_template("home.html")

if __name__ == "__main__":
    app.run(debug=True)
