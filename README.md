# FastAPI Product and Sales Management API

A simple FastAPI project for managing products and sales using in-memory storage.

## Features

* Create, retrieve, update, and delete products
* Register product sales
* Check product stock before creating a sale
* Filter sales by date
* Custom exception handling
* Request logging middleware
* Postman collection for API testing

## Installation

Clone the repository and install dependencies:

```bash
pip install -r requirements.txt
```

## Running the Application

Start the FastAPI server:

```bash
uvicorn main:app --reload
```

The API will be available at:

```text
http://127.0.0.1:8000
```

Interactive documentation:

```text
http://127.0.0.1:8000/docs
```

## Available Endpoints

### Products

| Method | Endpoint               | Description          |
| ------ | ---------------------- | -------------------- |
| POST   | /products              | Create a new product |
| GET    | /products              | Get all products     |
| GET    | /products/{product_id} | Get a product by ID  |
| PUT    | /products/{product_id} | Update a product     |
| DELETE | /products/{product_id} | Delete a product     |

### Sales

| Method | Endpoint               | Description          |
| ------ | ---------------------- | -------------------- |
| POST   | /sales                 | Create a new sale    |
| GET    | /sales                 | Get all sales        |
| GET    | /sales?date=YYYY-MM-DD | Filter sales by date |

## Testing

API requests were tested using Postman.

The Postman collection is included in the repository:

```text
FastAPI_Practice.postman_collection.json
```

## Notes

This project uses in-memory storage (Python dictionaries).

All data will be reset when the application restarts.
