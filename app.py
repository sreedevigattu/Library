import os
from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from models import db, Book, Genre
from utils import import_csv_data
import logging
from dateutil import parser as date_parser
from sqlalchemy import create_engine
import psycopg2
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get("DATABASE_URL")
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = os.urandom(24)

db.init_app(app)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@app.route('/')
def index():
    author = request.args.get('author', '')
    title = request.args.get('title', '')
    genres = request.args.getlist('genre')
    age_group = request.args.get('age_group', '')
    book_code = request.args.get('book_code', '')
    acc_num = request.args.get('acc_num', '')
    date_from = request.args.get('date_from', '')
    date_to = request.args.get('date_to', '')
    sort_by = request.args.get('sort_by', 'author')
    sort_order = request.args.get('sort_order', 'asc')
    
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    
    query = Book.query
    if author:
        query = query.filter(Book.author.ilike(f'%{author}%'))
    if title:
        query = query.filter(Book.title.ilike(f'%{title}%'))
    if genres:
        query = query.filter(Book.genres.any(Genre.name.in_(genres)))
    if age_group:
        query = query.filter(Book.age_group.ilike(f'%{age_group}%'))
    if book_code:
        query = query.filter(Book.book_code.ilike(f'%{book_code}%'))
    if acc_num:
        query = query.filter(Book.acc_num.ilike(f'%{acc_num}%'))
    if date_from:
        query = query.filter(Book.date_of_addition >= date_parser.parse(date_from).date())
    if date_to:
        query = query.filter(Book.date_of_addition <= date_parser.parse(date_to).date())
    
    if sort_by:
        column = getattr(Book, sort_by)
        if sort_order == 'desc':
            column = column.desc()
        query = query.order_by(column)
    
    pagination = query.paginate(page=page, per_page=per_page, error_out=False)
    books = pagination.items
    all_genres = Genre.query.all()
    
    return render_template('index.html', books=books, pagination=pagination, author=author, title=title, genres=genres,
                           age_group=age_group, book_code=book_code, acc_num=acc_num,
                           date_from=date_from, date_to=date_to, sort_by=sort_by, sort_order=sort_order, per_page=per_page,
                           all_genres=all_genres)

@app.route('/import_csv', methods=['GET', 'POST'])
def import_csv():
    if request.method == 'POST':
        if 'file' not in request.files:
            flash('No file part', 'error')
            return redirect(request.url)
        file = request.files['file']
        if file.filename == '':
            flash('No selected file', 'error')
            return redirect(request.url)
        if file and file.filename.endswith('.csv'):
            try:
                import_csv_data(file)
                flash('CSV data imported successfully', 'success')
            except ValueError as e:
                error_message = str(e)
                flash(f'Error importing CSV data: {error_message}', 'error')
                logger.error(f'CSV import error: {error_message}')
            except Exception as e:
                error_message = str(e)
                flash(f'Unexpected error during CSV import: {error_message}', 'error')
                logger.error(f'Unexpected CSV import error: {error_message}')
            return redirect(url_for('index'))
    return render_template('import_csv.html')

@app.route('/add_book', methods=['GET', 'POST'])
def add_book():
    if request.method == 'POST':
        try:
            engine = create_engine(app.config['SQLALCHEMY_DATABASE_URI'])
            connection = engine.connect()
            connection.close()
            logger.info("Database connection successful")

            price = request.form['price'].strip()
            if price == '' or not price.replace('.', '').isdigit():
                price = 0
            else:
                price = float(price)

            new_book = Book(
                author=request.form['author'],
                title=request.form['title'],
                price=price,
                age_group=request.form['age_group'],
                book_code=request.form['book_code'],
                acc_num=request.form['acc_num'],
                date_of_addition=date_parser.parse(request.form['date_of_addition']).date()
            )

            # Handle multiple genres
            genre_ids = request.form.getlist('genres')
            genres = Genre.query.filter(Genre.id.in_(genre_ids)).all()
            new_book.genres = genres

            db.session.add(new_book)
            db.session.commit()
            flash('New book added successfully', 'success')
            return redirect(url_for('index'))
        except psycopg2.OperationalError as e:
            db.session.rollback()
            error_message = f"Database connection error: {str(e)}"
            logger.error(error_message)
            flash(f'Error adding book: {error_message}', 'error')
        except Exception as e:
            db.session.rollback()
            error_message = str(e)
            logger.error(f'Error adding book: {error_message}')
            flash(f'Error adding book: {error_message}', 'error')
    genres = Genre.query.all()
    return render_template('add_book.html', genres=genres)

@app.route('/update_book/<int:id>', methods=['GET', 'POST'])
def update_book(id):
    book = Book.query.get_or_404(id)
    if request.method == 'POST':
        try:
            book.author = request.form['author']
            book.title = request.form['title']
            price = request.form['price'].strip()
            if price == '' or not price.replace('.', '').isdigit():
                price = 0
            else:
                price = float(price)
            book.price = price
            book.age_group = request.form['age_group']
            book.book_code = request.form['book_code']
            book.acc_num = request.form['acc_num']
            book.date_of_addition = date_parser.parse(request.form['date_of_addition']).date()

            # Handle multiple genres
            genre_ids = request.form.getlist('genres')
            genres = Genre.query.filter(Genre.id.in_(genre_ids)).all()
            book.genres = genres

            db.session.commit()
            flash('Book updated successfully', 'success')
            return redirect(url_for('index'))
        except Exception as e:
            flash(f'Error updating book: {str(e)}', 'error')
    genres = Genre.query.all()
    return render_template('update_book.html', book=book, genres=genres)

@app.route('/delete_book/<int:id>', methods=['POST'])
def delete_book(id):
    book = Book.query.get_or_404(id)
    try:
        db.session.delete(book)
        db.session.commit()
        flash('Book deleted successfully', 'success')
    except Exception as e:
        flash(f'Error deleting book: {str(e)}', 'error')
    return redirect(url_for('index'))

@app.route('/genres')
def get_genres():
    genres = Genre.query.all()
    return jsonify([{'id': genre.id, 'name': genre.name} for genre in genres])

@app.route('/test_db_connection')
def test_db_connection():
    try:
        engine = create_engine(app.config['SQLALCHEMY_DATABASE_URI'])
        connection = engine.connect()
        connection.close()
        return "Database connection successful", 200
    except Exception as e:
        return f"Database connection failed: {str(e)}", 500

@app.cli.command("update_schema")
def update_schema():
    with app.app_context():
        db.drop_all()
        db.create_all()
    print("Database schema updated successfully.")

def add_default_genres():
    default_genres = [
        "100 SERIES - TODDLERS", "8.08 Science Fiction/Fantasy", "9.00 Reference - Not For Issue",
        "8.02 Detective", "9.13 Nature/Environment", "7.01 Humour", "9.02 Hobbies",
        "1.22 Hindi Books For Issue", "8.06 Literary Fiction", "9.03 History/India",
        "6.51 Non Fiction English", "9.05 Literature And Arts", "8.03 Horror", "8.11 Graphic Novel",
        "1.21 Kannada Books For Issue", "7.51 Non Fiction - Biography", "7.03 Adventure/Mystery",
        "9.08 Science", "7.02 Science Fiction/Fantasy", "8.22 Fiction Hindi", "8.07 Romance",
        "1.00 Reference - Not For Issue", "6.53 Non Fiction Hindi", "7.11 Graphic Novel",
        "6.22 Fiction Hindi", "9.10 Miscellaneous", "1.01 English Books For Issue",
        "6.21 Fiction Kannada", "8.10 Miscellaneous", "8.05 Indian", "6.01 Fiction English",
        "9.11 Travel", "7.53 Non Fiction - Miscellaneous", "9.06 Philosophy, Spirituality And Religion",
        "9.12 Sports", "9.09 Self Help", "6.52 Non Fiction Kannada", "8.01 Classics",
        "6.24 Fiction Malayalam", "1.24 Malayalam Books For Issue", "1.20 Tamil Books For Issue",
        "8.04 Humour", "7.10 Miscellaneous Fiction", "8.09 Thriller", "9.04 Business/Economics",
        "6.11 Graphic Novel", "9.07 Psychology", "9.01 Auto/Biography"
    ]
    for genre_name in default_genres:
        genre = Genre.query.filter_by(name=genre_name).first()
        if not genre:
            new_genre = Genre(name=genre_name)
            db.session.add(new_genre)
    db.session.commit()

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        add_default_genres()
    app.run(host='0.0.0.0', port=5000, debug=True)
