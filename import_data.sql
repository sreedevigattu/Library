-- SQL script to import books data

-- Disable foreign key checks (if applicable)
-- SET CONSTRAINTS ALL DEFERRED;

-- Insert statements
INSERT INTO books (id, author, title, price, genre, age_group, book_code, acc_num, date_of_addition) VALUES (1, 'J.K. Rowling', 'Harry Potter and the Philosopher''s Stone', 15.99, 'Fantasy', 'Young Adult', 'HP001', 'ACC001', 1997-06-26);
INSERT INTO books (id, author, title, price, genre, age_group, book_code, acc_num, date_of_addition) VALUES (2, 'George Orwell', '1984', 12.99, 'Dystopian', 'Adult', 'GO001', 'ACC002', 1949-06-08);
INSERT INTO books (id, author, title, price, genre, age_group, book_code, acc_num, date_of_addition) VALUES (3, 'Jane Austen', 'Pride and Prejudice', 9.99, 'Romance', 'Adult', 'JA001', 'ACC003', 1813-01-28);
INSERT INTO books (id, author, title, price, genre, age_group, book_code, acc_num, date_of_addition) VALUES (4, 'Roald Dahl', 'Charlie and the Chocolate Factory', 8.99, 'Children''s Fiction', 'Children', 'RD001', 'ACC004', 1964-01-17);
INSERT INTO books (id, author, title, price, genre, age_group, book_code, acc_num, date_of_addition) VALUES (5, 'Agatha Christie', 'Murder on the Orient Express', 11.99, 'Mystery', 'Adult', 'AC001', 'ACC005', 1934-01-01);

-- Enable foreign key checks (if applicable)
-- SET CONSTRAINTS ALL IMMEDIATE;
