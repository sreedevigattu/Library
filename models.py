from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy import Column, Integer, String, Float, Date, Table, ForeignKey
from sqlalchemy.orm import relationship

class Base(DeclarativeBase):
    pass

db = SQLAlchemy(model_class=Base)

book_genre = Table('book_genre', Base.metadata,
    Column('book_id', Integer, ForeignKey('book.id'), primary_key=True),
    Column('genre_id', Integer, ForeignKey('genre.id'), primary_key=True)
)

class Book(db.Model):
    id = Column(Integer, primary_key=True)
    author = Column(String(100), nullable=False)
    title = Column(String(200), nullable=False)
    price = Column(Float, nullable=False)
    age_group = Column(String(50), nullable=False)
    book_code = Column(String(50), nullable=False)
    acc_num = Column(String(50), unique=True, nullable=False)
    date_of_addition = Column(Date, nullable=False)
    genres = relationship('Genre', secondary=book_genre, back_populates='books')

    def __repr__(self):
        return f'<Book {self.title} by {self.author}>'

class Genre(db.Model):
    id = Column(Integer, primary_key=True)
    name = Column(String(50), unique=True, nullable=False)
    books = relationship('Book', secondary=book_genre, back_populates='genres')

    def __repr__(self):
        return f'<Genre {self.name}>'
