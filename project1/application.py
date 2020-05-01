import os

from flask import Flask, session, render_template, request, send_from_directory, url_for
from flask_session import Session
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

app = Flask(__name__, static_folder='static')

# Check for environment variable
if not os.getenv("DATABASE_URL"):
    raise RuntimeError("DATABASE_URL is not set")

# Configure session to use filesystem
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Set up database
engine = create_engine(os.getenv("DATABASE_URL"))
db = scoped_session(sessionmaker(bind=engine))


@app.route("/")
def index():
    return render_template("index.html")

@app.route("/login")
def login():
    return render_template("login.html")

@app.route("/signin", methods=["GET", "POST"])
def signin():
    if request.method=="POST":
        return "Still not implemented the sign in"
    if request.method=="GET":
        return render_template("signin.html")
    return "Something went worn http method not suported"

@app.route('/css/<filename>')
def styles(filename):
    return send_from_directory("/templates/css/", filename)
