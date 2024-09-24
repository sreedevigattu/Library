import csv
from io import TextIOWrapper
from datetime import datetime
from models import db, Book
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def import_csv_data(file):
    csv_file = TextIOWrapper(file, encoding='utf-8')
    csv_reader = csv.DictReader(csv_file)
    
    required_fields = ['AUTHOR', 'TITLE', 'PRICE', 'GENRE', 'AGE_GROUP', 'BOOK_CODE', 'ACC_NUM', 'DATE_OF_ADDITION']
    
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
    
    db.session.commit()
    logger.info("CSV import completed successfully")
