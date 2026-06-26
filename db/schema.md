# Database Schema

## users
- id (PRIMARY KEY)
- email (NOT NULL, UNIQUE)
- full_name (NOT NULL)

Indexes:
- email

---

## products
- id (PRIMARY KEY)
- name (NOT NULL)
- price (NOT NULL, CHECK price > 0)
- stock (NOT NULL, CHECK stock >= 0)

---

## sales
- id (PRIMARY KEY)
- user_id (FOREIGN KEY -> users.id, NOT NULL)
- product_id (FOREIGN KEY -> products.id, NOT NULL)
- quantity (NOT NULL, CHECK quantity > 0)

Indexes:
- user_id
- product_id