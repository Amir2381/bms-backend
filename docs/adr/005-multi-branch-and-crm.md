# ADR-005: Multi-Branch and CRM Architecture

## Status

Accepted

## Context

The application has expanded from a flat, single-location sales model into a Business Intelligence platform. This required introducing tracking for distinct store locations (Branches) and tracking individual buyers (Customers) to calculate Customer Lifetime Value (CLV) and cross-selling potential.

Previously, `Sale` and `User` were globally scoped. Also, sales had no attached customer.

## Decision

### Multi-Branch Architecture
1. Introduce a `Branch` model.
2. Bind `User` and `Sale` directly to a `Branch`.
3. Provide a default fallback branch ("Main Branch") via Alembic migration to ensure backward compatibility and avoid database errors (`NOT NULL` constraints on existing data).

### CRM Module
1. Introduce a `Customer` model utilizing `phone` as a unique identifier.
2. Add an optional `customer_id` ForeignKey to `Sale`.
3. Introduce CRM endpoints (`/customers`) to manage these records.
4. Auto-attach or auto-create `Customer` records during the Data Import pipeline based on the optional `customer_phone` column.

## Consequences

### Positive
* Enables location-based analytics and role isolation in the future.
* Unlocks advanced analytics such as CLV, Top Customers, and Market Basket Analysis.
* Keeps legacy test flows intact by automatically routing unassigned objects to "Main Branch".

### Negative
* Additional complexity when creating a User (a `branch_id` is now strictly required).
* Database queries need to be carefully structured to aggregate customer behavior accurately.