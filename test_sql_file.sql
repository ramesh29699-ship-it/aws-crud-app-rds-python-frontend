show databases;

-- 1. Create the database
CREATE DATABASE IF NOT EXISTS prod;

-- 2. Select the database
USE prod;

-- 3. Create the products table matching your Python app
CREATE TABLE IF NOT EXISTS products (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    price DECIMAL(10, 2) NOT NULL,
    stock INT NOT NULL
);

INSERT INTO products (name, price, stock) VALUES 
('Raspberry Pi 5 Starter Kit', 120.00, 25),
('Ergonomic Vertical Mouse', 29.99, 80),
('Cloud Architect Exam Voucher', 150.00, 500),
('Studio Condenser Microphone', 199.50, 40),
('Mechanical Switch Tester', 15.00, 150);

Select * from products;
