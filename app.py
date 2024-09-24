import os
from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from models import db, Book
from utils import import_csv_data
import logging
from dateutil import parser as date_parser

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
    genre = request.args.get('genre', '')
    
    query = Book.query
    if author:
        query = query.filter(Book.author.ilike(f'%{author}%'))
    if title:
        query = query.filter(Book.title.ilike(f'%{title}%'))
    if genre:
        query = query.filter(Book.genre.ilike(f'%{genre}%'))
    
    books = query.all()
    return render_template('index.html', books=books, author=author, title=title, genre=genre)

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
            new_book = Book(
                author=request.form['author'],
                title=request.form['title'],
                price=float(request.form['price']),
                genre=request.form['genre'],
                age_group=request.form['age_group'],
                book_code=request.form['book_code'],
                acc_num=request.form['acc_num'],
                date_of_addition=date_parser.parse(request.form['date_of_addition']).date()
            )
            db.session.add(new_book)
            db.session.commit()
            flash('New book added successfully', 'success')
            return redirect(url_for('index'))
        except Exception as e:
            flash(f'Error adding book: {str(e)}', 'error')
    return render_template('add_book.html')

@app.route('/update_book/<int:id>', methods=['GET', 'POST'])
def update_book(id):
    book = Book.query.get_or_404(id)
    if request.method == 'POST':
        try:
            book.author = request.form['author']
            book.title = request.form['title']
            book.price = float(request.form['price'])
            book.genre = request.form['genre']
            book.age_group = request.form['age_group']
            book.book_code = request.form['book_code']
            book.acc_num = request.form['acc_num']
            book.date_of_addition = date_parser.parse(request.form['date_of_addition']).date()
            db.session.commit()
            flash('Book updated successfully', 'success')
            return redirect(url_for('index'))
        except Exception as e:
            flash(f'Error updating book: {str(e)}', 'error')
    return render_template('update_book.html', book=book)

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

@app.cli.command("update_schema")
def update_schema():
    with app.app_context():
        db.drop_all()
        db.create_all()
    print("Database schema updated successfully.")

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(host='0.0.0.0', port=8080, debug=True)
