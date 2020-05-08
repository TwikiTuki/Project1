import os

from flask import Flask, session, render_template, request, send_from_directory, url_for
from flask_session import Session
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Integer, String, Column

from tables import Book
import csv
import sys

max_books = int(sys.argv[-1])
print(f"max_books: {max_books}")

'''

app = Flask(__name__, static_folder='static')

# Check for environment variable
if not os.getenv("DATABASE_URL"):
    raise RuntimeError("DATABASE_URL is not set")

# Configure session to use filesystem
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

'''

engine = create_engine(os.getenv("DATABASE_URL"))
Session = sessionmaker(bind=engine)
session = Session()

Base = declarative_base()

# Read books.csv and create an ORM object list
with open("books.csv") as books_csv:
    books = csv.reader(books_csv)
    count = 1
    head = books.__next__()

    book_instances = []
    for book in books:

        # make dict
        dct = {}
        for i, key in enumerate(head):
            dct[key] = book[i]
        dct['year'] = int(dct['year'])

        # Make book object and append it to the list
        book_instances.append(Book(**dct))
        if (count % 100) == 0: print(count, end = " ")
        if count >= max_books: break
        count +=1
        # if count == 10: break
# Insert all books commit and close
print("\nINSERTING ... ")
session.add_all(book_instances)
session.commit()
session.close()
