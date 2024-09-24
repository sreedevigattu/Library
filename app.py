import os
from flask import Flask, render_template, request, redirect, url_for, flash
from models import db, Book
from utils import import_csv_data
import logging

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get("DATABASE_URL")
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = os.urandom(24)

db.init_app(app)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@app.route('/')
def index():
    books = Book.query.all()
    return render_template('index.html', books=books)

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
                flash(f'Error importing CSV data: {str(e)}', 'error')
                logger.error(f'CSV import error: {str(e)}')
            except Exception as e:
                flash(f'Unexpected error during CSV import: {str(e)}', 'error')
                logger.error(f'Unexpected CSV import error: {str(e)}')
            return redirect(url_for('index'))
    return render_template('import_csv.html')

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(host='0.0.0.0', port=5000, debug=True)
