-- Create the books table
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
