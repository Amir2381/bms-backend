CREATE TABLE users(
    id SERIAL PRIMARY KEY,
    email varchar(255) NOT NULL UNIQUE,
    full_name varchar(255) NOT NULL
);

CREATE TABLE products(
    id SERIAL PRIMARY KEY,
    name varchar(255) NOT NULL,
    price decimal(10, 2) NOT NULL CHECK(price > 0),
    stock integer NOT NULL CHECK(stock >= 0)
);

CREATE TABLE sales(
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL,
    product_id INTEGER NOT NULL,
    quantity INTEGER NOT NULL CHECK(quantity > 0),
    FOREIGN KEY (user_id) REFERENCES users(id),
    FOREIGN KEY (product_id) REFERENCES products(id)
);

INSERT INTO
    users(email, full_name)
VALUES
    ('amir@gmail.com', 'Amir'),
    ('ali@gmail.com', 'Ali'),
    ('akbar@gmail.com', 'Akbar');

INSERT INTO
    products(name, price, stock)
VALUES
    ('keyboard', 45.99, 10),
    ('mouse', 19.99, 25),
    ('monitor', 250.00, 5);

INSERT INTO
    sales (user_id, product_id, quantity)
VALUES
    (1, 2, 1),
    (2, 1, 3),
    (3, 3, 1);