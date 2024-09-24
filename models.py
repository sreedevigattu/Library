from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy import Column, Integer, String, Float, Date

class Base(DeclarativeBase):
    pass

db = SQLAlchemy(model_class=Base)

class Book(db.Model):
    id = Column(Integer, primary_key=True)
    author = Column(String(100), nullable=False)
    title = Column(String(200), nullable=False)
    price = Column(Float, nullable=False)
    genre = Column(String(50), nullable=False)
    age_group = Column(String(50), nullable=False)
    book_code = Column(String(20), nullable=False)
    acc_num = Column(String(20), unique=True, nullable=False)
    date_of_addition = Column(Date, nullable=False)

    def __repr__(self):
        return f'<Book {self.title} by {self.author}>'
