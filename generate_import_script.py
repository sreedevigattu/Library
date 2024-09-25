import os
import psycopg2
from psycopg2 import sql
from datetime import datetime

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

# Execute the SELECT query
cur.execute("SELECT * FROM books")

# Fetch all rows
rows = cur.fetchall()

# Get the column names
column_names = [desc[0] for desc in cur.description]

# Generate SQL INSERT statements
insert_statements = []
for row in rows:
    values = []
    for value in row[1:]:  # Skip the id column
        if isinstance(value, str):
            value_updated = value.replace("'", "''")
            values.append(f"'{value_updated}'")
        elif isinstance(value, datetime):
            values.append(f"'{value.strftime('%Y-%m-%d')}'")
        elif value is None:
            values.append('NULL')
        else:
            values.append(str(value))

    columns = ', '.join(column_names[1:])  # Skip the id column
    values_str = ', '.join(values)
    insert_statements.append(
        f"INSERT INTO books ({columns}) VALUES ({values_str});")

# Write to SQL file
with open('import_data.sql', 'w') as sqlfile:
    sqlfile.write("-- SQL script to import books data\n\n")
    sqlfile.write("-- Disable foreign key checks (if applicable)\n")
    sqlfile.write("-- SET CONSTRAINTS ALL DEFERRED;\n\n")
    sqlfile.write("-- Insert statements\n")
    for statement in insert_statements:
        sqlfile.write(statement + "\n")
    sqlfile.write("\n-- Enable foreign key checks (if applicable)\n")
    sqlfile.write("-- SET CONSTRAINTS ALL IMMEDIATE;\n")

# Close the database connection
cur.close()
conn.close()

print("SQL import script generated successfully as 'import_data.sql'")
