from dataclasses import dataclass
from datetime import date
from decimal import Decimal


@dataclass(frozen=True)
class SummaryMetrics:
    total_sales: Decimal
    total_transactions: int
    average_order_value: Decimal
    highest_sale: Decimal | None
    lowest_sale: Decimal | None
    average_daily_sales: Decimal
    sold_products_count: int


@dataclass(frozen=True)
class SalesTrendPoint:
    period: date
    revenue: Decimal
    transaction_count: int


@dataclass(frozen=True)
class SalesTrend:
    points: list[SalesTrendPoint]


@dataclass(frozen=True)
class ProductPerformance:
    product_id: int
    product_name: str
    quantity_sold: int
    revenue: Decimal
    revenue_share: Decimal


@dataclass(frozen=True)
class ProductPerformanceResult:
    products: list[ProductPerformance]


@dataclass(frozen=True)
class CategoryPerformance:
    category_id: int | None
    category_name: str
    quantity_sold: int
    revenue: Decimal
    revenue_share: Decimal


@dataclass(frozen=True)
class CategoryPerformanceResult:
    categories: list[CategoryPerformance]


@dataclass(frozen=True)
class SalespersonPerformance:
    user_id: int
    user_name: str
    quantity_sold: int
    revenue: Decimal
    transaction_count: int


@dataclass(frozen=True)
class SalespersonPerformanceResult:
    salespersons: list[SalespersonPerformance]
