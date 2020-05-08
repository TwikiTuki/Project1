import os

from flask import Flask, session, render_template, request, send_from_directory, url_for, redirect
from flask_session import Session
from sqlalchemy import create_engine, and_
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy import Integer, String, Column, TEXT
from sqlalchemy.ext.declarative import declarative_base

from tables import Book, User, Review
app = Flask(__name__, static_folder='static', template_folder='templates')

app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0

# Check for environment variable
if not os.getenv("DATABASE_URL"):
    raise RuntimeError("DATABASE_URL is not set")

# Key for encripting
app.config["SECRET_KEY"] = "OCML3BRawWEUeaxcuKHLpw"

# Configure session to use filesystem
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Set up database
engine = create_engine(os.getenv("DATABASE_URL"))
db = scoped_session(sessionmaker(bind=engine))

# Get all the usernames
user_names = []

def logged():
    user_name = session.get("USER_NAME")
    user = db.query(User).filter_by(user_name=user_name).first()
    return user
app.jinja_env.globals.update(logged=logged, str=str)

@app.route("/", methods=["GET", "POST"])
def index():
    return render_template("index.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    form = request.form
    user_name=form.get("user_name")
    user = db.query(User).filter_by(user_name=form.get("user_name")).first()
    print(user_name, user)
    if not user or user.password != form.get("password"):
        return render_template("login.html", error=True)
    else:
        session.pop("USER_NAME")
        if session.get("COMMENT"): session.pop("COMMENT")
        session["USER_NAME"] = user_name
        return render_template("search.html", error=False)

@app.route("/logout")
def logout():
    print("session USER_NAME: ", session.get("USER_NAME"))
    session.pop("USER_NAME")
    session.pop("COMMENT")
    print("session USER_NAME: ", session.get("USER_NAME"))
    return render_template("index.html")


@app.route("/signin", methods=["GET", "POST"])
def signin():
    # GET method
    if request.method=="GET":
        return render_template("signin.html")
    # POST method
    elif request.method=="POST":
        # Check password
        form = request.form
        password = form.getlist("password")
        if (len(password) != 2) or (password[0] != password[1]) or not password[0]:
            return render_template("err.html", error = "Error in password, check you entered it twice correctly")
        else:
            password = password[0]

        #check first and second names
        first_name = form.get("first_name")
        second_name = form.get("second_name")
        if not first_name or not second_name:
            return render_template("err.html", error = "Enter your first and second names")

        # Check username
        user_name = form.get("user_name")
        if not user_name:
            return render_template("err.html", error = "Enter your username")
        elif user_name in user_names:
            return render_template("err.html", user_name = f"{user_name} has already been picked")

        # Add user to the database
        user = User(first_name = first_name, second_name = second_name, user_name = user_name, password = password)
        try:
            db.add(user)
            db.commit()
            users = db.query(Book).all()# to debug
            return render_template('search.html')
        except:
            db.rollback()
            raise
            return render_template("err.html", error = "SORRY something whent wrong")

    # Not GET nor POST methods
    else:
        return "Something went worg http method not suported"

# Search
@app.route('/search', methods=['GET', 'POST'])
def search():
    if request.method == 'GET':
        books = []
    elif request.method == 'POST':
        if not (logged()):
            return render_template("err.html", error = "You are not logged in")
        form = request.form
        title = form.get('title')
        author = form.get('author')
        isbn = form.get('isbn')
        books = db.query(Book).filter(and_(Book.isbn.like(f"%{isbn}%"), Book.title.like(f"%{title}%"), Book.author.like(f"%{author}%"))).all()
        books = [book.print_dicc() for book in books]
    else:
        return "Something went worg http method not suported"

    return render_template('search.html', books = books)

@app.route("/book/<isbn>", methods=["GET", "POST"])
def book(isbn):
    comments = []
    book = db.query(Book).filter_by(isbn = isbn).first()
    if not book:
        return "No such book", 404

    reviews = db.query(Review).filter_by(book_isbn = isbn).all()
    reviews = [[r.comment, r.user_id] for r in reviews]
    if request.method == "GET":
        print("rev", reviews, reviews[0][0])
        return render_template("book.html",
            isbn=book.isbn,
            title=book.title,
            author=book.author,
            comments=comments,
            reviews = reviews,
            aRate=0,
            nVotes=0
            )
    # If method is POST
    elif request.method == "POST":
        form = request.form
        user_name = session.get("USER_NAME")
        user = db.query(User).filter_by(user_name=user_name).first()
        user_id = user.id
        comment = session.get("COMMENT")
        if comment: session.pop("COMMENT") # THI IS SHIT. But otherwise the cookie will never be removed
        print("session: ", session.get("COMMENT"))
        # Set the comment and the rate to be writen of the books

        # If cookie exists the is Second try to create comment
        #(First time will be False. comment_err.html must have been called)
        print('sdaf')
        if comment:
            args = request.args
            if args.get('override'):
                print("OVERRIDE: ", args.get('override')) #just for
                comment = comment['comment']
                rate = comment['rate']
            elif args.get('ignore'):
                print("IGNORE: ", args.get('ignore')) #just for debbugging
                return render_template("book.html")
            else:
                return render_template('book.html')
        # If cookie does not exists
        else:
            print('elsa')
            comment = form.get("comment")
            rate = form.get("rate")
        print('fasd')

        # CHECK OK TO INSERT DATA
        # Check if all data has been supplied
        if not (comment and rate):
            print(f"comment:{comment}, rate: {rate}")
            session["COMMENT"] = {
                'isbn': isbn,
                'comment': comment,
                'rate': rate
                }
            return render_template("comment_err.html", err = "no_data")
        # Finnaly check if a comment already exists
        elif db.query(Review).filter_by(user_id = user_id, book_isbn = isbn).first():
                    session["COMMENT"] = {'isbn': isbn,
                        'comment': comment,
                        'rate': rate
                        }
                    return render_template("comment_err.html", err = "exists", isbn = isbn)
        # INSERT DATA
        else:
            print("inserting")
            comment = form.get('comment')
            rate = form.get('rate')

            # Crete ans save the review
            review = Review(
                book_isbn = isbn,
                user_id = user_id,
                rate = rate,
                comment = comment
            )
            try:
                print("try")
                db.add(review)
                db.commit()
            except:
                print('except')
                db.rollback()
                raise
        # insert the comment
        reviews = db.query(Review).filter_by(book_isbn = isbn).all()
        reviews = [[r.comment, r.user_id] for r in reviews]
        if request.method == "GET":
            print("rev", reviews, reviews[0][0])
            return render_template("book.html",
                isbn=book.isbn,
                title=book.title,
                author=book.author,
                comments=comments,
                reviews = reviews,
                aRate=0,
                nVotes=0
                )
