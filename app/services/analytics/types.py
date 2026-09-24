from dataclasses import dataclass
from datetime import date
from decimal import Decimal


@dataclass(frozen=True)
class SummaryMetrics:
    total_sales: Decimal
    total_profit: Decimal
    profit_margin: Decimal
    total_transactions: int
    average_order_value: Decimal
    highest_sale: Decimal | None
    lowest_sale: Decimal | None
    average_daily_sales: Decimal
    sold_products_count: int
    average_clv: Decimal


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


@dataclass(frozen=True)
class CustomerPerformance:
    customer_id: int
    customer_name: str
    customer_phone: str
    revenue: Decimal
    profit: Decimal
    transaction_count: int


@dataclass(frozen=True)
class CustomerPerformanceResult:
    customers: list[CustomerPerformance]


@dataclass(frozen=True)
class CrossSellRecommendation:
    product_id: int
    product_name: str
    frequency: int


@dataclass(frozen=True)
class ProductCrossSell:
    product_id: int
    product_name: str
    recommendations: list[CrossSellRecommendation]


@dataclass(frozen=True)
class CrossSellingResult:
    items: list[ProductCrossSell]
