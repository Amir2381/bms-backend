# ADR-001: Sale Domain Model

## Status

Accepted

## Context

The initial sales model represented a sale using a single product and quantity directly on the `sales` table.

This model is simple, but it does not represent a real-world sale containing multiple products. It also makes item-level analytics and historical price tracking harder to support.

A sale may contain multiple products, and the price paid for a product must remain historically accurate even if the product's current price changes later.

## Decision

Represent the sales domain using two entities:

* `Sale`
* `SaleItem`

A `Sale` belongs to a user and contains one or more `SaleItem` records.

Each `SaleItem` contains:

* `product_id`
* `quantity`
* `unit_price`

The `unit_price` is stored as a snapshot of the product price at the time of the sale.

## Consequences

### Positive

* A single sale can contain multiple products.
* Sale-level and item-level analytics are both possible.
* Historical sale prices remain accurate.
* The domain model better represents the real business concept of a sale.

### Negative

* The model is more complex than storing product and quantity directly on `Sale`.
* Queries involving sale details require a relationship with `SaleItem`.
* More code and tests are required compared with the simpler model.

## Alternatives Considered

### Keep the original Sale model

Keep `product_id` and `quantity` directly on `Sale`.

This would be simpler for the current MVP, but it would incorrectly model multi-product sales and create limitations for future analytics.

### Decision

The `Sale + SaleItem` model was selected because the additional complexity is justified by the actual business domain and expected future requirements.
