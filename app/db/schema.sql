CREATE TABLE users(
    id SERIAL PRIMARY KEY,
    email varchar(255) NOT NULL UNIQUE,
    full_name varchar(255) NOT NULL,
    hashed_password varchar(255) NOT NULL
);

CREATE TABLE products(
    id SERIAL PRIMARY KEY,
    name varchar(255) NOT NULL,
    price decimal(10, 2) NOT NULL,
    stock integer NOT NULL
);

CREATE TABLE sales(
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL,
    sale_date timestamp with time zone NOT NULL,
    created_at timestamp with time zone NOT NULL,
    FOREIGN KEY (user_id) REFERENCES users(id)
);

CREATE TABLE sale_items(
    id SERIAL PRIMARY KEY,
    sale_id INTEGER NOT NULL,
    product_id INTEGER NOT NULL,
    quantity INTEGER NOT NULL,
    unit_price decimal(10, 2) NOT NULL,
    FOREIGN KEY (sale_id) REFERENCES sales(id),
    FOREIGN KEY (product_id) REFERENCES products(id)
);