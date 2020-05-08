from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import create_engine, Integer, String, Column, TEXT, ForeignKey
from sqlalchemy.orm import relationship
import json
import os

# Create the engine
if __name__ == "__main__":
    engine = create_engine(os.getenv("DATABASE_URL"))

# DEFINE CLASSES
Base = declarative_base()
class User(Base):
    ''' Table containing all the users that have been regitered '''
    __tablename__ = 'users'
    id = Column(Integer, primary_key = True)
    first_name = Column(String, nullable = False)
    second_name = Column(String, nullable = False)
    user_name = Column(String, nullable = False)
    password = Column(String, nullable = False)
    reviews = relationship("Review")
    def print_dict(self):
        dicc ={
            'first_name': self.first_name,
            'second_name':self.second_name,
            'user_name': self.user_name,
            'password': self.password
        }
        return dicc


class Book(Base):
    ''' Table containing the Books. Must be populated with import.py called by import.bs '''
    __tablename__ = 'books'
    isbn = Column(String(13), primary_key = True)
    title = Column(String)
    author = Column(String)
    year = Column(Integer)
    reviews = relationship("Review")

    def print_dicc(self):
        dicc = {
            'isbn': self.isbn,
            'title': self.title,
            'author': self.author,
            'year': self.year
        }
        return dicc
# Create books and users tables before reviews
if __name__ == "__main__":
    Base.metadata.create_all(engine)


class Review(Base):
    ''' Table containing all the reviews made by the users '''
    __tablename__ = 'reviews'
    id = Column(Integer, primary_key = True)
    user_id = Column(Integer, ForeignKey('users.id'))
    book_isbn = Column(String(13), ForeignKey("books.isbn"))
    rate = Column(String, nullable = False)
    comment = Column(TEXT, nullable = True)
    user = relationship("User", back_populates="reviews")
    user = relationship("Book", back_populates="reviews")

if __name__ == "__main__":
    # Create the tables
    Base.metadata.create_all(engine)
