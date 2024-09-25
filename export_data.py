+import os
import csv
import psycopg2
from psycopg2 import sql

# Database connection parameters
db_params = {
    'dbname': os.environ.get('PGDATABASE'),
    'user': os.environ.get('PGUSER'),
    'password': os.environ.get('PGPASSWORD'),
    'host': os.environ.get('PGHOST'),
    'port': os.environ.get('PGPORT')
}

# Connect to the database
conn = psycopg2.connect(**db_params)
cur = conn.cursor()

# Create the books table if it doesn't exist
create_table_query = """
CREATE TABLE IF NOT EXISTS books (
    id SERIAL PRIMARY KEY,
    author VARCHAR(100) NOT NULL,
    title VARCHAR(200) NOT NULL,
    price FLOAT NOT NULL,
    genre VARCHAR(50) NOT NULL,
    age_group VARCHAR(50) NOT NULL,
    book_code VARCHAR(50) NOT NULL,
    acc_num VARCHAR(50) UNIQUE NOT NULL,
    date_of_addition DATE NOT NULL
);
"""
cur.execute(create_table_query)
conn.commit()

# Execute the SELECT query
cur.execute("SELECT * FROM books")

# Fetch all rows
rows = cur.fetchall()

# Get the column names
column_names = [desc[0] for desc in cur.description]

# Write to CSV file
with open('exported_books.csv', 'w', newline='') as csvfile:
    csvwriter = csv.writer(csvfile)
    
    # Write the header
    csvwriter.writerow(column_names)
    
    # Write the data rows
    csvwriter.writerows(rows)

# Close the database connection
cur.close()
conn.close()

print("Data exported successfully to 'exported_books.csv'")
