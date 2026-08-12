# BMS Backend

A FastAPI-based backend for managing products, users, and sales.

The project uses PostgreSQL for persistent data storage, SQLAlchemy as the ORM, Alembic for database migrations, and JWT-based authentication.

## Features

- User registration and authentication
- JWT-based authentication
- Product CRUD operations
- Product stock management
- Sales management
- Automatic stock reduction when creating a sale
- Historical unit-price snapshots for sales
- Sale timestamps
- Product filtering and pagination
- SQLAlchemy ORM and Repository Pattern
- Centralized application configuration
- Request and application logging
- Custom exception handling
- Database migrations with Alembic
- Automated tests with pytest

## Tech Stack

- Python
- FastAPI
- SQLAlchemy
- PostgreSQL
- Alembic
- Pydantic
- pydantic-settings
- JWT
- pytest

## Project Structure

```text
app/
├── core/          # Configuration, security, dependencies, logging
├── db/            # Database engine and session management
├── models/        # SQLAlchemy ORM models
├── repositories/  # Database access layer
├── routers/       # API endpoints
├── schemas/       # Pydantic request/response schemas
└── main.py        # FastAPI application entry point
```

## Installation

Clone the repository and create a virtual environment:

```bash
python -m venv venv
```

Activate the virtual environment on Windows:

```powershell
venv\Scripts\Activate.ps1
```

Install the dependencies:

```bash
pip install -r requirements.txt
```

## Configuration

Create a `.env` file based on `.env.example`:

```powershell
Copy-Item .env.example .env
```

Then update the values in `.env`:

```env
DATABASE_URL=postgresql+psycopg://username:password@localhost:5432/database_name
SECRET_KEY=your-secret-key
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
SQL_ECHO=false
```

> **Important:** Never commit the `.env` file or real secrets to the repository.

## Database

The application currently uses PostgreSQL.

Make sure PostgreSQL is running and create the database specified in `DATABASE_URL`.

Database schema changes are managed with Alembic.

Apply the latest migrations:

```bash
alembic upgrade head
```

Check the current migration:

```bash
alembic current
```

View migration history:

```bash
alembic history
```

## Running the Application

Start the development server:

```bash
uvicorn app.main:app --reload
```

The API will be available at:

```text
http://127.0.0.1:8000
```

Interactive API documentation:

```text
http://127.0.0.1:8000/docs
```

## API Endpoints

### Authentication

| Method | Endpoint | Description                                    |
| ------ | -------- | ---------------------------------------------- |
| POST   | `/login` | Authenticate a user and obtain an access token |

### Users

| Method | Endpoint           | Description      |
| ------ | ------------------ | ---------------- |
| POST   | `/users`           | Create a user    |
| GET    | `/users`           | Get all users    |
| GET    | `/users/{user_id}` | Get a user by ID |

### Products

| Method | Endpoint                 | Description                                |
| ------ | ------------------------ | ------------------------------------------ |
| POST   | `/products`              | Create a product                           |
| GET    | `/products`              | Get products with filtering and pagination |
| GET    | `/products/{product_id}` | Get a product by ID                        |
| PUT    | `/products/{product_id}` | Update a product                           |
| DELETE | `/products/{product_id}` | Delete a product                           |

### Sales

| Method | Endpoint           | Description      |
| ------ | ------------------ | ---------------- |
| POST   | `/sales`           | Create a sale    |
| GET    | `/sales`           | Get all sales    |
| GET    | `/sales/{sale_id}` | Get a sale by ID |
| DELETE | `/sales/{sale_id}` | Delete a sale    |

## Testing

Run the complete test suite with:

```bash
python -m pytest
```

The test suite covers the main product, sales, and user functionality.

## Database Migrations

When a database model changes, create a new migration:

```bash
alembic revision --autogenerate -m "describe your change"
```

Always review the generated migration before applying it.

Apply the migration:

```bash
alembic upgrade head
```

Roll back the latest migration:

```bash
alembic downgrade -1
```

## Development Status

The project is currently under active development.

The current focus is improving the backend foundation, data model, database migrations, testing, and maintainability before adding data import and analytics functionality.