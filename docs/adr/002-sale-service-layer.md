# ADR-002: Sale Service Layer

## Status

Accepted

## Context

Creating a sale involves multiple business rules:

* The user must exist.
* Each product must exist.
* Sufficient stock must be available.
* Product stock must be reduced.
* The current product price must be captured as the sale item's historical unit price.
* The sale and its items must be persisted together.

Keeping these rules inside the API router would couple business logic to the HTTP layer and make the logic harder to test and reuse.

## Decision

Business logic for creating a sale is implemented in a dedicated service layer.

The current flow is:

Router → Sale Service → Repository → Database

The router is responsible for HTTP-level orchestration and translating domain-specific exceptions into HTTP responses.

The service is responsible for enforcing sales business rules.

Repositories are responsible for database access.

## Consequences

### Positive

* Business logic is separated from HTTP concerns.
* Service logic can be tested independently from API behavior.
* Routers remain small and easier to understand.
* Business rules can be reused by other application entry points in the future.
* Database access remains separated through repositories.

### Negative

* Adds an additional application layer.
* Some simple operations may require more files and indirection.

## Decision

A simple Service Layer is used without introducing additional abstractions or frameworks.

The design intentionally avoids over-engineering while keeping business rules separate from the API layer.
