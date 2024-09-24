import csv
from io import TextIOWrapper
from datetime import datetime
from models import db, Book
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def read_first_5_lines(file):
    file.seek(0)
    return [next(file).decode('utf-8') for _ in range(5)]

def import_csv_data(file):
    filename = file.filename
    logger.info(f"Importing CSV file: {filename}")
    
    first_5_lines = read_first_5_lines(file)
    logger.info(f"First 5 lines of the CSV:\n{''.join(first_5_lines)}")
    
    file.seek(0)
    csv_file = TextIOWrapper(file, encoding='utf-8')
    
    required_fields = ['AUTHOR', 'TITLE', 'PRICE', 'GENRE', 'AGE_GROUP', 'BOOK_CODE', 'ACC_NUM', 'DATE_OF_ADDITION']
    
    try:
        csv_reader = csv.DictReader(csv_file)
        
        for row_num, row in enumerate(csv_reader, start=1):
            try:
                # Check if all required fields are present
                missing_fields = [field for field in required_fields if field not in row]
                if missing_fields:
                    raise KeyError(f"Missing required fields: {', '.join(missing_fields)}")
                
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
                logger.info(f"Successfully processed row {row_num}")
            except KeyError as e:
                logger.error(f"Row {row_num}: {str(e)}")
                raise ValueError(f"Row {row_num}: Missing required field(s) - {str(e)}")
            except ValueError as e:
                logger.error(f"Row {row_num}: Invalid data format - {str(e)}")
                raise ValueError(f"Row {row_num}: Invalid data format - {str(e)}")
            except Exception as e:
                logger.error(f"Row {row_num}: Unexpected error - {str(e)}")
                raise ValueError(f"Row {row_num}: Unexpected error - {str(e)}")
    except csv.Error as e:
        logger.error(f"CSV parsing error: {str(e)}")
        raise ValueError(f"CSV parsing error: {str(e)}")
    
    db.session.commit()
    logger.info("CSV import completed successfully")
