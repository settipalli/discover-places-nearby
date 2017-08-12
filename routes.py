# Will contain the applications main code.

from flask import Flask, render_template, request
from models import db
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
    if request.method == "GET":
        form = SignupForm()
        return render_template("signup.html", form=form)

    elif request.method == "POST":
        return "Success!"


if __name__ == "__main__":
    app.run(debug=True)
