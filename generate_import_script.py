import os
import psycopg2
from psycopg2 import sql
from datetime import datetime
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Database connection parameters
db_params = {
    'dbname': os.environ.get('PGDATABASE'),
    'user': os.environ.get('PGUSER'),
    'password': os.environ.get('PGPASSWORD'),
    'host': os.environ.get('PGHOST'),
    'port': os.environ.get('PGPORT')
}

logger.info("Connecting to the database...")

try:
    # Connect to the database
    conn = psycopg2.connect(**db_params)
    cur = conn.cursor()

    logger.info("Connected successfully.")

    # Check if the books table exists
    cur.execute("SELECT to_regclass('public.books')")
    table_exists = cur.fetchone()[0]

    if not table_exists:
        logger.info("Books table does not exist. Creating it...")
        with open('create_table.sql', 'r') as create_table_file:
            create_table_sql = create_table_file.read()
        cur.execute(create_table_sql)
        conn.commit()
        logger.info("Books table created successfully.")

    # Execute the SELECT query to fetch all data
    cur.execute("SELECT * FROM books")

    # Fetch all rows
    rows = cur.fetchall()

    logger.info(f"Fetched {len(rows)} rows from the books table.")

    # Get the column names
    column_names = [desc[0] for desc in cur.description]

    # Generate SQL INSERT statements
    insert_statements = []
    for row in rows:
        values = []
        for value in row:
            if isinstance(value, str):
                value_updated = value.replace("'", "''")
                values.append(f"'{value_updated}'")
            elif isinstance(value, datetime):
                values.append(f"'{value.strftime('%Y-%m-%d')}'")
            elif value is None:
                values.append('NULL')
            else:
                values.append(str(value))

        columns = ', '.join(column_names)
        values_str = ', '.join(values)
        insert_statements.append(
            f"INSERT INTO books ({columns}) VALUES ({values_str});")

    logger.info(f"Generated {len(insert_statements)} INSERT statements.")

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

    logger.info("SQL import script generated successfully as 'import_data.sql'")

except Exception as e:
    logger.error(f"An error occurred: {str(e)}")

finally:
    # Close the database connection
    if 'cur' in locals():
        cur.close()
    if 'conn' in locals():
        conn.close()
    logger.info("Database connection closed.")

print("Script execution completed.")
