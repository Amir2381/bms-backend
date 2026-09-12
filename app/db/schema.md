# Database Schema

## users

* id (PRIMARY KEY)
* email (NOT NULL, UNIQUE)
* full_name (NOT NULL)
* hashed_password (NOT NULL)

Indexes:

* email

---

## products

* id (PRIMARY KEY)
* name (NOT NULL)
* price (NOT NULL)
* stock (NOT NULL)

---

## sales

* id (PRIMARY KEY)
* user_id (FOREIGN KEY -> users.id, NOT NULL)
* sale_date (NOT NULL)
* created_at (NOT NULL)

Indexes:

* user_id

---

## sale_items

* id (PRIMARY KEY)
* sale_id (FOREIGN KEY -> sales.id, NOT NULL)
* product_id (FOREIGN KEY -> products.id, NOT NULL)
* quantity (NOT NULL)
* unit_price (NOT NULL)

Relationships:

* One `User` can have many `Sale` records.
* One `Sale` can have many `SaleItem` records.
* One `Product` can appear in many `SaleItem` records.
* `SaleItem.unit_price` stores the product price at the time of the sale.
