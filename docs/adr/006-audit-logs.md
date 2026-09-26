# ADR-006: Audit Logs System

## Status

Accepted

## Context

As the system scales and supports batch data imports and manual price modifications, it is crucial to maintain an immutable history of sensitive operations. Administrators need to track who performed specific actions (like importing a CSV or changing a product's price), when it happened, and what the exact changes were.

## Decision

We introduced an `AuditLog` database model to serve as a centralized ledger for system-wide operations.

The entity contains:
* `user_id`: The ID of the user who performed the action.
* `action`: A string identifier for the operation (e.g., `IMPORT_SALES`, `UPDATE_PRODUCT_PRICE`).
* `entity_type` & `entity_id`: Polymorphic identifiers to attach the log to a specific domain model.
* `details`: A JSON column to store arbitrary payload and change diffs (e.g., `old_price` and `new_price`).
* `timestamp`: The exact UTC time of the operation.

## Consequences

### Positive
* Complete traceability of sensitive actions.
* The JSON column provides flexibility, meaning we do not need to alter the database schema to track different details for different actions.
* Simplifies compliance and debugging.

### Negative
* The database size will grow faster due to the logging of operations.
* Developers must remember to manually instantiate and save `AuditLog` records for newly added sensitive operations.