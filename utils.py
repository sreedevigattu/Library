import csv
from io import TextIOWrapper
from datetime import datetime
from models import db, Book

def import_csv_data(file):
    csv_file = TextIOWrapper(file, encoding='utf-8')
    csv_reader = csv.DictReader(csv_file)
    
    for row in csv_reader:
        book = Book(
            author=row['AUTHOR'],
            title=row['TITLE'],
            price=float(row['PRICE']),
            genre=row['GENRE'],
            age_group=row['AGE_GROUP'],
            book_code=row['BOOK_CODE'],
            acc_num=row['ACC_NUM'],
            date_of_addition=datetime.strptime(row['DATE_OF_ADDITION'], '%Y-%m-%d').date()
        )
        db.session.add(book)
    
    db.session.commit()
